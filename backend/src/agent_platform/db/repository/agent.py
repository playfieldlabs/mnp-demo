from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.agent import Agent, AgentRun
from agent_platform.db.repository.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: AsyncSession):
        super().__init__(Agent, session)

    async def get_by_name(self, name: str) -> Agent | None:
        result = await self.session.execute(select(Agent).where(Agent.name == name))
        return result.scalar_one_or_none()


class AgentRunRepository(BaseRepository[AgentRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(AgentRun, session)

    async def get_by_agent_id(
        self, agent_id: str, limit: int | None = None, offset: int | None = None
    ) -> list[AgentRun]:
        query = (
            select(AgentRun)
            .where(AgentRun.agent_id == agent_id)
            .order_by(AgentRun.started_at.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
