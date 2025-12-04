from typing import Any

from agent_platform.common.v1.types_pb2 import PaginationResponse
from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.tool import Tool as ToolModel
from agent_platform.db.repository.tool import ToolRepository
from agent_platform.service.v1.tool_service_connect import ToolService
from agent_platform.service.v1.tool_service_pb2 import (
    CreateToolResponse,
    DeleteToolResponse,
    GetToolResponse,
    ListToolsResponse,
    UpdateToolResponse,
)


class ToolServiceImpl(ToolService):
    def __init__(self) -> None:
        pass

    async def create_tool(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: ToolRepository = ToolRepository(session)
            tool: ToolModel = await repo.create(
                id=request.tool.id or None,
                name=request.tool.name,
                input_schema=dict(request.tool.input_schema),
                output_schema=dict(request.tool.output_schema),
                context=request.tool.context,
            )
            await session.commit()
            return CreateToolResponse(tool=self._db_to_proto(tool))

    async def get_tool(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: ToolRepository = ToolRepository(session)
            tool: ToolModel | None = await repo.get_by_id(request.tool_id)
            if not tool:
                raise ValueError(f"Tool {request.tool_id} not found")
            return GetToolResponse(tool=self._db_to_proto(tool))

    async def list_tools(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: ToolRepository = ToolRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            tools: list[ToolModel] = await repo.get_all(limit=page_size, offset=0)
            return ListToolsResponse(
                tools=[self._db_to_proto(t) for t in tools],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(tools),
                ),
            )

    async def update_tool(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: ToolRepository = ToolRepository(session)
            tool: ToolModel | None = await repo.update(
                request.tool.id,
                name=request.tool.name,
                input_schema=dict(request.tool.input_schema),
                output_schema=dict(request.tool.output_schema),
                context=request.tool.context,
            )
            if tool is None:
                raise ValueError(f"Tool {request.tool.id} not found")
            await session.commit()
            return UpdateToolResponse(tool=self._db_to_proto(tool))

    async def delete_tool(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: ToolRepository = ToolRepository(session)
            await repo.delete(request.tool_id)
            await session.commit()
            return DeleteToolResponse()

    def _db_to_proto(self, tool_db: ToolModel) -> Any:
        import json

        from google.protobuf.struct_pb2 import Struct

        from agent_platform.tool.v1.tool_pb2 import Tool as ToolProto

        input_struct: Struct = Struct()
        input_struct.update(json.loads(json.dumps(tool_db.input_schema)))
        output_struct: Struct = Struct()
        output_struct.update(json.loads(json.dumps(tool_db.output_schema)))

        return ToolProto(
            id=tool_db.id,
            name=tool_db.name,
            input_schema=input_struct,
            output_schema=output_struct,
            context=tool_db.context,
        )
