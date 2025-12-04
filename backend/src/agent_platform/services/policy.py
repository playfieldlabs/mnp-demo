from typing import Any

from agent_platform.common.v1.types_pb2 import PaginationResponse
from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.policy import PolicyAgent, PolicyRun
from agent_platform.db.repository.policy import PolicyAgentRepository, PolicyRunRepository
from agent_platform.service.v1.policy_service_connect import PolicyService
from agent_platform.service.v1.policy_service_pb2 import (
    CreatePolicyAgentResponse,
    DeletePolicyAgentResponse,
    GetPolicyAgentResponse,
    GetPolicyRunResponse,
    ListPolicyAgentsResponse,
    ListPolicyRunsResponse,
    RunPolicyAgentResponse,
    UpdatePolicyAgentResponse,
)


class PolicyServiceImpl(PolicyService):
    def __init__(self) -> None:
        pass

    async def create_policy_agent(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyAgentRepository = PolicyAgentRepository(session)
            policy: PolicyAgent = await repo.create(
                id=request.policy_agent.id or None,
                name=request.policy_agent.name,
                system_prompt=request.policy_agent.system_prompt,
                policy_tool=dict(request.policy_agent.policy_tool)
                if request.policy_agent.policy_tool
                else None,
                data_source_ids=list(request.policy_agent.data_source_ids),
                external_source_config=dict(request.policy_agent.external_source_config)
                if request.policy_agent.external_source_config
                else None,
                output_schema=dict(request.policy_agent.output_schema)
                if request.policy_agent.output_schema
                else None,
                update_schedule=request.policy_agent.update_schedule,
            )
            await session.commit()
            return CreatePolicyAgentResponse(policy_agent=self._db_to_proto(policy))

    async def get_policy_agent(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyAgentRepository = PolicyAgentRepository(session)
            policy: PolicyAgent | None = await repo.get_by_id(request.policy_agent_id)
            if not policy:
                raise ValueError(f"Policy agent {request.policy_agent_id} not found")
            return GetPolicyAgentResponse(policy_agent=self._db_to_proto(policy))

    async def list_policy_agents(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyAgentRepository = PolicyAgentRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            policies: list[PolicyAgent] = await repo.get_all(limit=page_size, offset=0)
            return ListPolicyAgentsResponse(
                policy_agents=[self._db_to_proto(p) for p in policies],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(policies),
                ),
            )

    async def update_policy_agent(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyAgentRepository = PolicyAgentRepository(session)
            policy: PolicyAgent | None = await repo.update(
                request.policy_agent.id,
                name=request.policy_agent.name,
                system_prompt=request.policy_agent.system_prompt,
                policy_tool=dict(request.policy_agent.policy_tool)
                if request.policy_agent.policy_tool
                else None,
                data_source_ids=list(request.policy_agent.data_source_ids),
                external_source_config=dict(request.policy_agent.external_source_config)
                if request.policy_agent.external_source_config
                else None,
                output_schema=dict(request.policy_agent.output_schema)
                if request.policy_agent.output_schema
                else None,
                update_schedule=request.policy_agent.update_schedule,
            )
            if policy is None:
                raise ValueError(f"Policy agent {request.policy_agent.id} not found")
            await session.commit()
            return UpdatePolicyAgentResponse(policy_agent=self._db_to_proto(policy))

    async def delete_policy_agent(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyAgentRepository = PolicyAgentRepository(session)
            await repo.delete(request.policy_agent_id)
            await session.commit()
            return DeletePolicyAgentResponse()

    async def run_policy_agent(self, request, ctx):
        import uuid
        from datetime import datetime

        async with AsyncSessionLocal() as session:
            repo: PolicyRunRepository = PolicyRunRepository(session)
            run: PolicyRun = await repo.create(
                id=str(uuid.uuid4()),
                policy_agent_id=request.policy_agent_id,
                started_at=datetime.utcnow(),
                status="RUNNING",
            )
            await session.commit()
            return RunPolicyAgentResponse(policy_run=self._db_run_to_proto(run))

    async def get_policy_run(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyRunRepository = PolicyRunRepository(session)
            run_id: str | None = getattr(request, "run_id", None) or getattr(
                request, "policy_run_id", None
            )
            if run_id is None:
                raise ValueError("run_id or policy_run_id is required")
            run: PolicyRun | None = await repo.get_by_id(run_id)
            if not run:
                raise ValueError(f"Policy run {run_id} not found")
            return GetPolicyRunResponse(policy_run=self._db_run_to_proto(run))

    async def list_policy_runs(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PolicyRunRepository = PolicyRunRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            runs: list[PolicyRun] = await repo.get_by_policy_agent_id(
                request.policy_agent_id, limit=page_size, offset=0
            )
            return ListPolicyRunsResponse(
                policy_runs=[self._db_run_to_proto(r) for r in runs],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(runs),
                ),
            )

    def _db_to_proto(self, policy_db: PolicyAgent) -> Any:
        import json

        from google.protobuf.struct_pb2 import Struct
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.policy.v1.policy_pb2 import (
            PolicyAgent as PolicyAgentProto,
        )

        policy_tool: Struct | None = None
        if policy_db.policy_tool:
            policy_tool = Struct()
            policy_tool.update(json.loads(json.dumps(policy_db.policy_tool)))

        external_config: Struct | None = None
        if policy_db.external_source_config:
            external_config = Struct()
            external_config.update(json.loads(json.dumps(policy_db.external_source_config)))

        output_schema: Struct | None = None
        if policy_db.output_schema:
            output_schema = Struct()
            output_schema.update(json.loads(json.dumps(policy_db.output_schema)))

        last_updated: Timestamp | None = None
        if policy_db.last_updated:
            last_updated = Timestamp()
            last_updated.FromDatetime(policy_db.last_updated)

        return PolicyAgentProto(
            id=policy_db.id,
            name=policy_db.name,
            system_prompt=policy_db.system_prompt,
            policy_tool=policy_tool,
            data_source_ids=policy_db.data_source_ids,
            external_source_config=external_config,
            output_schema=output_schema,
            update_schedule=policy_db.update_schedule,
            last_updated=last_updated,
        )

    def _db_run_to_proto(self, run_db: PolicyRun) -> Any:
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.policy.v1.policy_pb2 import (
            PolicyRun as PolicyRunProto,
        )

        started_at: Timestamp = Timestamp()
        started_at.FromDatetime(run_db.started_at)
        finished_at: Timestamp | None = None
        if run_db.finished_at:
            finished_at = Timestamp()
            finished_at.FromDatetime(run_db.finished_at)

        return PolicyRunProto(
            id=run_db.id,
            policy_agent_id=run_db.policy_agent_id,
            started_at=started_at,
            finished_at=finished_at,
            status=run_db.status,
            policy_content=run_db.policy_content or "",
            error_message=run_db.error_message or "",
        )
