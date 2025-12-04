from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform.db.models.dataset import Dataset, PromptDataset
from agent_platform.db.repository.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    def __init__(self, session: AsyncSession):
        super().__init__(Dataset, session)

    async def get_by_name(self, name: str) -> Dataset | None:
        result = await self.session.execute(select(Dataset).where(Dataset.name == name))
        return result.scalar_one_or_none()


class PromptDatasetRepository(BaseRepository[PromptDataset]):
    def __init__(self, session: AsyncSession):
        super().__init__(PromptDataset, session)

    async def get_by_name(self, name: str) -> PromptDataset | None:
        result = await self.session.execute(select(PromptDataset).where(PromptDataset.name == name))
        return result.scalar_one_or_none()
