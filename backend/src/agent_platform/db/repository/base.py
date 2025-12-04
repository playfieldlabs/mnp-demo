from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model: type[ModelType] = model
        self.session: AsyncSession = session
        mapper = sa_inspect(model)
        primary_keys = mapper.primary_key
        if not primary_keys:
            raise ValueError(f"Model {model} does not have a primary key")
        self._primary_key_column = primary_keys[0]

    async def create(self, **kwargs: Any) -> ModelType:
        instance: ModelType = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: str) -> ModelType | None:
        result = await self.session.execute(
            select(self.model).where(self._primary_key_column == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[ModelType]:
        query = select(self.model)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, id: str, **kwargs: Any) -> ModelType | None:
        await self.session.execute(
            update(self.model).where(self._primary_key_column == id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self._primary_key_column == id)
        )
        await self.session.flush()
        rowcount: int | None = getattr(result, "rowcount", None)
        return rowcount is not None and rowcount > 0

    async def count(self) -> int:
        result = await self.session.execute(select(self.model))
        return len(list(result.scalars().all()))
