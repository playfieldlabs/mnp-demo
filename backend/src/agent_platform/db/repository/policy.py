from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.policy import PolicyAgent, PolicyRun
from agent_platform.db.repository.base import BaseRepository


class PolicyAgentRepository(BaseRepository[PolicyAgent]):
    def __init__(self, session: AsyncSession):
        super().__init__(PolicyAgent, session)

    async def get_by_name(self, name: str) -> PolicyAgent | None:
        result = await self.session.execute(select(PolicyAgent).where(PolicyAgent.name == name))
        return result.scalar_one_or_none()


class PolicyRunRepository(BaseRepository[PolicyRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(PolicyRun, session)

    async def get_by_policy_agent_id(
        self, policy_agent_id: str, limit: int | None = None, offset: int | None = None
    ) -> list[PolicyRun]:
        query = (
            select(PolicyRun)
            .where(PolicyRun.policy_agent_id == policy_agent_id)
            .order_by(PolicyRun.started_at.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
