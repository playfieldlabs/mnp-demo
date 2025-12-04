from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.tool import Tool
from agent_platform.db.repository.base import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tool, session)

    async def get_by_name(self, name: str) -> Tool | None:
        result = await self.session.execute(select(Tool).where(Tool.name == name))
        return result.scalar_one_or_none()
