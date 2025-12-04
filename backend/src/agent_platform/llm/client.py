from collections.abc import AsyncIterator
from typing import Any

from anthropic import AsyncAnthropic
from anthropic._types import Omit
from anthropic.types import MessageParam, ToolParam

from agent_platform.config import settings


class AnthropicClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.client: AsyncAnthropic = AsyncAnthropic(api_key=api_key or settings.anthropic_api_key)

    async def create_message(
        self,
        model: str,
        messages: list[MessageParam],
        tools: list[ToolParam] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ):
        return await self.client.messages.create(
            model=model,
            messages=messages,
            tools=tools if tools is not None else Omit(),
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system is not None else Omit(),
        )

    async def stream_message(
        self,
        model: str,
        messages: list[MessageParam],
        tools: list[ToolParam] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> AsyncIterator[Any]:
        async with self.client.messages.stream(
            model=model,
            messages=messages,
            tools=tools if tools is not None else Omit(),
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system is not None else Omit(),
        ) as stream:
            async for event in stream:
                yield event
