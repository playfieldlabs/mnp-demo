from agent_platform.tools.base import Tool


class ToolNotFoundError(Exception):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.id] = tool

    async def get_tool(self, tool_id: str) -> Tool:
        if tool_id not in self._tools:
            raise ToolNotFoundError(f"Tool {tool_id} not found")
        return self._tools[tool_id]

    async def get_tools(self, tool_ids: list[str]) -> list[Tool]:
        tools: list[Tool] = []
        for tool_id in tool_ids:
            if tool_id not in self._tools:
                raise ToolNotFoundError(f"Tool {tool_id} not found")
            tools.append(self._tools[tool_id])
        return tools

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())
