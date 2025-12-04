from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.benchmark import BenchmarkRun
from agent_platform.db.repository.base import BaseRepository


class BenchmarkRunRepository(BaseRepository[BenchmarkRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(BenchmarkRun, session)

    async def get_by_agent_id(
        self, agent_id: str, limit: int | None = None, offset: int | None = None
    ) -> list[BenchmarkRun]:
        query = (
            select(BenchmarkRun)
            .where(BenchmarkRun.agent_id == agent_id)
            .order_by(BenchmarkRun.started_at.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_dataset_id(
        self, dataset_id: str, limit: int | None = None, offset: int | None = None
    ) -> list[BenchmarkRun]:
        query = (
            select(BenchmarkRun)
            .where(BenchmarkRun.prompt_dataset_id == dataset_id)
            .order_by(BenchmarkRun.started_at.desc())
        )
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
