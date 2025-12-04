from agent_platform.tools.base import Tool


class ToolNotFoundError(Exception):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.id] = tool

    async def get_tool(self, tool_id: str) -> Tool:
        tool = self._tools.get(tool_id)
        if tool is None:
            raise ToolNotFoundError(f"Tool {tool_id} not found")
        return tool

    async def get_tools(self, tool_ids: list[str]) -> list[Tool]:
        tools: list[Tool] = []
        for tool_id in tool_ids:
            tool: Tool | None = self._tools.get(tool_id)
            if tool is None:
                raise ToolNotFoundError(f"Tool {tool_id} not found")
            tools.append(tool)
        return tools

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())
