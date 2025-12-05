from datetime import datetime
from typing import Any

from google.protobuf.timestamp_pb2 import Timestamp

from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.agent import Agent, AgentRun
from agent_platform.db.repository.agent import AgentRepository, AgentRunRepository
from agent_platform.llm.executor import AgentExecutor
from agent_platform.models.agent import AgentModel
from agent_platform.models.agent_config import AgentConfig
from agent_platform.service.v1.agent_service_connect import AgentService


class AgentServiceImpl(AgentService):
    def __init__(self, executor: AgentExecutor) -> None:
        self.executor: AgentExecutor = executor

    async def create_agent(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            CreateAgentResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRepository(session)
            agent = await repo.create(
                id=request.agent.id or None,
                name=request.agent.name,
                task=request.agent.task,
                tool_ids=list(request.agent.tool_ids),
                system_prompt=request.agent.system_prompt,
                policy_agent_ids=list(request.agent.policy_agent_ids),
                config={
                    "model": request.agent.config.model,
                    "temperature": request.agent.config.temperature,
                    "max_tokens": request.agent.config.max_tokens,
                    "max_tool_calls": request.agent.config.max_tool_calls,
                },
            )
            await session.commit()

            agent_proto = self._db_to_proto(agent)
            return CreateAgentResponse(agent=agent_proto)

    async def get_agent(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            GetAgentResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRepository(session)
            agent = await repo.get_by_id(request.agent_id)
            if not agent:
                raise ValueError(f"Agent {request.agent_id} not found")

            agent_proto = self._db_to_proto(agent)
            return GetAgentResponse(agent=agent_proto)

    async def list_agents(self, request, ctx):
        from agent_platform.common.v1.types_pb2 import PaginationResponse
        from agent_platform.service.v1.agent_service_pb2 import (
            ListAgentsResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            agents: list[Agent] = await repo.get_all(limit=page_size, offset=0)
            total: int = await repo.count()

            agents_proto = [self._db_to_proto(agent) for agent in agents]
            pagination = PaginationResponse(
                next_page_token="",
                total_count=total,
            )
            return ListAgentsResponse(agents=agents_proto, pagination=pagination)

    async def update_agent(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            UpdateAgentResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRepository(session)
            agent: Agent | None = await repo.update(
                request.agent.id,
                name=request.agent.name,
                task=request.agent.task,
                tool_ids=list(request.agent.tool_ids),
                system_prompt=request.agent.system_prompt,
                policy_agent_ids=list(request.agent.policy_agent_ids),
                config={
                    "model": request.agent.config.model,
                    "temperature": request.agent.config.temperature,
                    "max_tokens": request.agent.config.max_tokens,
                    "max_tool_calls": request.agent.config.max_tool_calls,
                },
            )
            if agent is None:
                raise ValueError(f"Agent {request.agent.id} not found")
            await session.commit()

            agent_proto = self._db_to_proto(agent)
            return UpdateAgentResponse(agent=agent_proto)

    async def delete_agent(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            DeleteAgentResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRepository(session)
            await repo.delete(request.agent_id)
            await session.commit()
            return DeleteAgentResponse()

    async def run_agent(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            RunAgentResponse,
        )

        async with AsyncSessionLocal() as session:
            agent_repo = AgentRepository(session)
            agent_db = await agent_repo.get_by_id(request.agent_id)
            if not agent_db:
                raise ValueError(f"Agent {request.agent_id} not found")

            agent = self._db_to_agent_model(agent_db)
            agent_run = await self.executor.run_agent(
                agent,
                request.input,
                list(request.dataset_ids),
            )

            run_repo = AgentRunRepository(session)
            run_db = await run_repo.create(**self._agent_run_to_dict(agent_run))
            await session.commit()

            agent_run_proto = self._db_run_to_proto(run_db)
            return RunAgentResponse(agent_run=agent_run_proto)

    async def stream_agent_run(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            StreamAgentRunResponse,
        )

        async with AsyncSessionLocal() as session:
            agent_repo = AgentRepository(session)
            agent_db = await agent_repo.get_by_id(request.agent_id)
            if not agent_db:
                raise ValueError(f"Agent {request.agent_id} not found")

            agent = self._db_to_agent_model(agent_db)
            async for event in self.executor.stream_agent_run(
                agent,
                request.input,
                list(request.dataset_ids),
            ):
                if "block" in event and event["block"] is not None:
                    block_proto = self._dict_to_block_proto(event["block"])
                    yield StreamAgentRunResponse(block=block_proto)
                elif "completed" in event and event["completed"] is not None:
                    yield StreamAgentRunResponse(completed=event["completed"])
                elif "error" in event and event["error"] is not None:
                    yield StreamAgentRunResponse(error=event["error"])

    async def get_agent_run(self, request, ctx):
        from agent_platform.service.v1.agent_service_pb2 import (
            GetAgentRunResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRunRepository(session)
            run = await repo.get_by_id(request.run_id)
            if not run:
                raise ValueError(f"Agent run {request.run_id} not found")

            run_proto = self._db_run_to_proto(run)
            return GetAgentRunResponse(agent_run=run_proto)

    async def list_agent_runs(self, request, ctx):
        from agent_platform.common.v1.types_pb2 import PaginationResponse
        from agent_platform.service.v1.agent_service_pb2 import (
            ListAgentRunsResponse,
        )

        async with AsyncSessionLocal() as session:
            repo = AgentRunRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            runs: list[AgentRun] = await repo.get_by_agent_id(
                request.agent_id, limit=page_size, offset=0
            )

            runs_proto = [self._db_run_to_proto(run) for run in runs]
            pagination = PaginationResponse(
                next_page_token="",
                total_count=len(runs),
            )
            return ListAgentRunsResponse(agent_runs=runs_proto, pagination=pagination)

    def _db_to_proto(self, agent_db: Agent) -> Any:
        from agent_platform.agent.v1.agent_pb2 import Agent as AgentProto
        from agent_platform.agent.v1.agent_pb2 import AgentConfig

        created_at: Timestamp = Timestamp()
        created_at.FromDatetime(agent_db.created_at)
        updated_at: Timestamp = Timestamp()
        updated_at.FromDatetime(agent_db.updated_at)

        config_dict: dict = agent_db.config
        config: AgentConfig = AgentConfig(
            model=config_dict["model"],
            temperature=config_dict["temperature"],
            max_tokens=config_dict["max_tokens"],
            max_tool_calls=config_dict["max_tool_calls"],
        )

        return AgentProto(
            id=agent_db.id,
            name=agent_db.name,
            task=agent_db.task,
            tool_ids=agent_db.tool_ids,
            system_prompt=agent_db.system_prompt,
            policy_agent_ids=agent_db.policy_agent_ids,
            config=config,
            created_at=created_at,
            updated_at=updated_at,
        )

    def _db_to_agent_model(self, agent_db: Agent) -> AgentModel:
        config_dict: dict = agent_db.config
        config: AgentConfig = AgentConfig(
            model=config_dict["model"],
            temperature=config_dict["temperature"],
            max_tokens=config_dict["max_tokens"],
            max_tool_calls=config_dict["max_tool_calls"],
        )
        return AgentModel(
            id=agent_db.id,
            name=agent_db.name,
            task=agent_db.task,
            tool_ids=agent_db.tool_ids,
            system_prompt=agent_db.system_prompt,
            policy_agent_ids=agent_db.policy_agent_ids,
            config=config,
        )

    def _agent_run_to_dict(self, agent_run: AgentRun) -> dict[str, Any]:
        return {
            "id": agent_run.id,
            "agent_id": agent_run.agent_id,
            "started_at": agent_run.started_at,
            "finished_at": agent_run.finished_at,
            "blocks": agent_run.blocks,
            "force_final_tool_call": agent_run.force_final_tool_call,
            "status": agent_run.status,
            "dataset_ids": agent_run.dataset_ids,
            "metrics": agent_run.metrics,
            "error_message": agent_run.error_message,
        }

    def _dict_to_block_proto(self, block_dict: dict[str, Any]) -> Any:
        import json

        from google.protobuf.duration_pb2 import Duration
        from google.protobuf.struct_pb2 import Struct
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.agent.v1.block_pb2 import (
            AssistantMessage,
            Block,
            ThinkingBlock,
            UserInput,
        )
        from agent_platform.tool.v1.tool_call_pb2 import ToolCall

        block = Block(id=block_dict["id"], sequence=block_dict["sequence"])

        if "user_input" in block_dict:
            user_input_dict: dict[str, Any] = block_dict["user_input"]
            user_input = UserInput(text=user_input_dict["text"])
            block.user_input.CopyFrom(user_input)
        elif "assistant_message" in block_dict:
            assistant_dict: dict[str, Any] = block_dict["assistant_message"]
            assistant_message = AssistantMessage(text=assistant_dict["text"])
            block.assistant_message.CopyFrom(assistant_message)
        elif "thinking_block" in block_dict:
            thinking_dict: dict[str, Any] = block_dict["thinking_block"]
            signature: str = ""
            if "signature" in thinking_dict:
                signature = thinking_dict["signature"]
            thinking_block = ThinkingBlock(
                thinking=thinking_dict["thinking"],
                signature=signature,
            )
            block.thinking_block.CopyFrom(thinking_block)
        elif "tool_call" in block_dict:
            tool_call_dict: dict[str, Any] = block_dict["tool_call"]
            tool_call = ToolCall(
                id=tool_call_dict["id"],
                tool_id=tool_call_dict["tool_id"],
            )

            input_struct: Struct = Struct()
            input_struct.update(json.loads(json.dumps(tool_call_dict["input"])))
            tool_call.input.CopyFrom(input_struct)

            output_struct: Struct = Struct()
            output_struct.update(json.loads(json.dumps(tool_call_dict["output"])))
            tool_call.output.CopyFrom(output_struct)

            if "started_at" in tool_call_dict:
                started_at_value: Any = tool_call_dict["started_at"]
                started_at: Timestamp = Timestamp()
                if isinstance(started_at_value, datetime):
                    started_at.FromDatetime(started_at_value)
                elif isinstance(started_at_value, str):
                    started_at.FromDatetime(datetime.fromisoformat(started_at_value.replace('Z', '+00:00')))
                tool_call.started_at.CopyFrom(started_at)

            if "duration" in tool_call_dict:
                duration: Duration = Duration()
                duration.seconds = int(tool_call_dict["duration"])
                tool_call.duration.CopyFrom(duration)

            block.tool_call.CopyFrom(tool_call)

        return block

    def _db_run_to_proto(self, run_db: AgentRun) -> Any:
        from agent_platform.agent.v1.agent_run_pb2 import (
            AgentRun as AgentRunProto,
        )

        started_at: Timestamp = Timestamp()
        started_at.FromDatetime(run_db.started_at)
        finished_at: Timestamp | None = None
        if run_db.finished_at:
            finished_at = Timestamp()
            finished_at.FromDatetime(run_db.finished_at)

        blocks_proto: list[Any] = [self._dict_to_block_proto(b) for b in run_db.blocks]

        return AgentRunProto(
            id=run_db.id,
            agent_id=run_db.agent_id,
            started_at=started_at,
            finished_at=finished_at,
            blocks=blocks_proto,
            force_final_tool_call=run_db.force_final_tool_call,
            status=run_db.status,
            dataset_ids=run_db.dataset_ids,
            metrics=run_db.metrics,
            error_message=run_db.error_message,
        )
