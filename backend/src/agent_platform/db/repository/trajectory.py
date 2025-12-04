from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.trajectory import Trajectory
from agent_platform.db.repository.base import BaseRepository


class TrajectoryRepository(BaseRepository[Trajectory]):
    def __init__(self, session: AsyncSession):
        super().__init__(Trajectory, session)

    async def get_by_agent_id(
        self, agent_id: str, limit: int | None = None, offset: int | None = None
    ) -> list[Trajectory]:
        query = (
            select(Trajectory)
            .where(Trajectory.agent_id == agent_id)
            .order_by(Trajectory.created_at.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
