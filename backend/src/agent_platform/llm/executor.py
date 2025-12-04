import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import TYPE_CHECKING

from anthropic.types import (
    CitationsDelta,
    ContentBlockDeltaEvent,
    ContentBlockStartEvent,
    InputJSONDelta,
    MessageParam,
    SignatureDelta,
    TextDelta,
    ThinkingBlock,
    ThinkingDelta,
    ToolParam,
)

from agent_platform.db.models.agent import AgentRun
from agent_platform.llm.client import AnthropicClient
from agent_platform.models.agent import AgentModel
from agent_platform.models.agent_config import AgentConfig
from agent_platform.tools.base import Tool
from agent_platform.tools.registry import ToolRegistry

if TYPE_CHECKING:
    ContentBlockDelta = TextDelta | InputJSONDelta | CitationsDelta | ThinkingDelta | SignatureDelta


class Status:
    AWAITING_START = 0
    RUNNING = 1
    DONE = 2
    ERROR = 3


class AgentExecutor:
    def __init__(self, llm_client: AnthropicClient, tool_registry: ToolRegistry):
        self.llm_client = llm_client
        self.tool_registry = tool_registry

    async def run_agent(
        self,
        agent: AgentModel,
        input_text: str,
        dataset_ids: list[str] | None = None,
    ) -> AgentRun:
        run_id: str = str(uuid.uuid4())
        started_at: datetime = datetime.utcnow()
        blocks: list[dict] = []
        tool_call_count: int = 0
        status: int = Status.RUNNING

        try:
            tools: list[Tool] = await self.tool_registry.get_tools(agent.tool_ids)
            tool_params: list[ToolParam] = [self._tool_to_param(tool) for tool in tools]

            messages: list[MessageParam] = [{"role": "user", "content": input_text}]

            blocks.append(
                {"id": str(uuid.uuid4()), "sequence": 0, "user_input": {"text": input_text}}
            )

            config: AgentConfig = agent.config
            max_tool_calls: int = config.max_tool_calls
            max_tokens: int = config.max_tokens
            temperature: float = config.temperature
            model: str = config.model

            for iteration in range(max_tool_calls + 1):
                response = await self.llm_client.create_message(
                    model=model,
                    messages=messages,
                    tools=tool_params if tool_params else None,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=agent.system_prompt,
                )

                assistant_content: str = ""
                for content_block in response.content:
                    if content_block.type == "text":
                        assistant_content += content_block.text
                    elif isinstance(content_block, ThinkingBlock):
                        blocks.append(
                            {
                                "id": str(uuid.uuid4()),
                                "sequence": len(blocks),
                                "thinking_block": {
                                    "thinking": content_block.thinking,
                                    "signature": content_block.signature,
                                },
                            }
                        )

                if assistant_content:
                    blocks.append(
                        {
                            "id": str(uuid.uuid4()),
                            "sequence": len(blocks),
                            "assistant_message": {"text": assistant_content},
                        }
                    )
                    messages.append({"role": "assistant", "content": assistant_content})

                if not response.stop_reason or response.stop_reason != "tool_use":
                    break

                for tool_use in response.content:
                    if tool_use.type != "tool_use":
                        continue

                    tool_call_id: str = str(uuid.uuid4())
                    tool: Tool = await self.tool_registry.get_tool(tool_use.name)
                    tool_input: dict = tool_use.input
                    tool_started: datetime = datetime.utcnow()
                    tool_output: dict = await tool.execute(tool_input)
                    tool_finished: datetime = datetime.utcnow()
                    tool_duration: float = (tool_finished - tool_started).total_seconds()

                    blocks.append(
                        {
                            "id": str(uuid.uuid4()),
                            "sequence": len(blocks),
                            "tool_call": {
                                "id": tool_call_id,
                                "tool_id": tool_use.name,
                                "input": tool_input,
                                "output": tool_output,
                                "started_at": tool_started,
                                "duration": tool_duration,
                            },
                        }
                    )

                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": str(tool_output),
                                }
                            ],
                        }
                    )

                    tool_call_count += 1

            status = Status.DONE

        except Exception as e:
            status = Status.ERROR
            error_message: str | None = str(e)
        else:
            error_message = None

        finished_at: datetime = datetime.utcnow()

        return AgentRun(
            id=run_id,
            agent_id=agent.id,
            started_at=started_at,
            finished_at=finished_at,
            blocks=blocks,
            status=status,
            dataset_ids=dataset_ids or [],
            metrics={
                "tool_call_count": tool_call_count,
            },
            error_message=error_message if status == Status.ERROR else None,
        )

    async def stream_agent_run(
        self,
        agent: AgentModel,
        input_text: str,
        dataset_ids: list[str] | None = None,
    ) -> AsyncIterator[dict]:
        run_id: str = str(uuid.uuid4())
        started_at: datetime = datetime.utcnow()
        sequence: int = 0

        try:
            tools: list[Tool] = await self.tool_registry.get_tools(agent.tool_ids)
            tool_params: list[ToolParam] = [self._tool_to_param(tool) for tool in tools]

            messages: list[MessageParam] = [{"role": "user", "content": input_text}]

            yield {
                "block": {
                    "id": str(uuid.uuid4()),
                    "sequence": sequence,
                    "user_input": {"text": input_text},
                }
            }
            sequence += 1

            config: AgentConfig = agent.config
            max_tokens: int = config.max_tokens
            temperature: float = config.temperature
            model: str = config.model

            thinking_blocks: dict[int, str] = {}
            thinking_signatures: dict[int, str] = {}
            async for event in self.llm_client.stream_message(
                model=model,
                messages=messages,
                tools=tool_params if tool_params else None,
                max_tokens=max_tokens,
                temperature=temperature,
                system=agent.system_prompt,
            ):
                if isinstance(event, ContentBlockStartEvent):
                    if isinstance(event.content_block, ThinkingBlock):
                        start_block_index: int = event.index
                        thinking_blocks[start_block_index] = event.content_block.thinking
                        thinking_signatures[start_block_index] = event.content_block.signature
                        yield {
                            "block": {
                                "id": str(uuid.uuid4()),
                                "sequence": sequence,
                                "thinking_block": {
                                    "thinking": event.content_block.thinking,
                                    "signature": event.content_block.signature,
                                },
                            }
                        }
                        sequence += 1
                elif isinstance(event, ContentBlockDeltaEvent):
                    delta: (
                        TextDelta | InputJSONDelta | CitationsDelta | ThinkingDelta | SignatureDelta
                    ) = event.delta
                    delta_block_index: int = event.index
                    if isinstance(delta, TextDelta) and delta.text is not None:
                        yield {
                            "block": {
                                "id": str(uuid.uuid4()),
                                "sequence": sequence,
                                "assistant_message": {"text": delta.text},
                            }
                        }
                        sequence += 1
                    elif isinstance(delta, ThinkingDelta) and delta.thinking is not None:
                        if delta_block_index not in thinking_blocks:
                            thinking_blocks[delta_block_index] = ""
                        thinking_blocks[delta_block_index] += delta.thinking
                        signature: str = thinking_signatures.get(delta_block_index, "")
                        yield {
                            "block": {
                                "id": str(uuid.uuid4()),
                                "sequence": sequence,
                                "thinking_block": {
                                    "thinking": thinking_blocks[delta_block_index],
                                    "signature": signature,
                                },
                            }
                        }
                        sequence += 1

        except Exception as e:
            yield {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}

        finished_at: datetime = datetime.utcnow()
        yield {
            "completed": {
                "id": run_id,
                "agent_id": agent.id,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "status": 2,
                "dataset_ids": dataset_ids or [],
            }
        }

    def _tool_to_param(self, tool: Tool) -> ToolParam:
        return {
            "name": tool.name,
            "description": tool.context,
            "input_schema": tool.input_schema,
        }
