from typing import Any

from agent_platform.common.v1.types_pb2 import PaginationResponse
from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.dataset import Dataset, PromptDataset
from agent_platform.db.repository.dataset import DatasetRepository, PromptDatasetRepository
from agent_platform.service.v1.dataset_service_connect import DatasetService
from agent_platform.service.v1.dataset_service_pb2 import (
    CreateDatasetResponse,
    CreatePromptDatasetResponse,
    DeleteDatasetResponse,
    GetDatasetResponse,
    GetPromptDatasetResponse,
    ListDatasetsResponse,
    ListPromptDatasetsResponse,
)


class DatasetServiceImpl(DatasetService):
    def __init__(self) -> None:
        pass

    async def create_dataset(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: DatasetRepository = DatasetRepository(session)
            dataset: Dataset = await repo.create(name=request.name, files=[])
            await session.commit()
            return CreateDatasetResponse(dataset=self._db_to_proto(dataset))

    async def get_dataset(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: DatasetRepository = DatasetRepository(session)
            dataset: Dataset | None = await repo.get_by_id(request.dataset_id)
            if not dataset:
                raise ValueError(f"Dataset {request.dataset_id} not found")
            return GetDatasetResponse(dataset=self._db_to_proto(dataset))

    async def list_datasets(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: DatasetRepository = DatasetRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            datasets: list[Dataset] = await repo.get_all(limit=page_size, offset=0)
            return ListDatasetsResponse(
                datasets=[self._db_to_proto(d) for d in datasets],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(datasets),
                ),
            )

    async def delete_dataset(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: DatasetRepository = DatasetRepository(session)
            await repo.delete(request.dataset_id)
            await session.commit()
            return DeleteDatasetResponse()

    async def create_prompt_dataset(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PromptDatasetRepository = PromptDatasetRepository(session)
            dataset: PromptDataset = await repo.create(name=request.name)
            await session.commit()
            return CreatePromptDatasetResponse(prompt_dataset=self._db_prompt_to_proto(dataset))

    async def get_prompt_dataset(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PromptDatasetRepository = PromptDatasetRepository(session)
            dataset: PromptDataset | None = await repo.get_by_id(request.prompt_dataset_id)
            if not dataset:
                raise ValueError(f"Prompt dataset {request.prompt_dataset_id} not found")
            return GetPromptDatasetResponse(prompt_dataset=self._db_prompt_to_proto(dataset))

    async def list_prompt_datasets(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: PromptDatasetRepository = PromptDatasetRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            datasets: list[PromptDataset] = await repo.get_all(limit=page_size, offset=0)
            return ListPromptDatasetsResponse(
                prompt_datasets=[self._db_prompt_to_proto(d) for d in datasets],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(datasets),
                ),
            )

    def _db_to_proto(self, dataset_db: Dataset) -> Any:
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.dataset.v1.dataset_pb2 import Dataset as DatasetProto

        created_at: Timestamp = Timestamp()
        created_at.FromDatetime(dataset_db.created_at)
        updated_at: Timestamp = Timestamp()
        updated_at.FromDatetime(dataset_db.updated_at)

        return DatasetProto(
            id=dataset_db.id,
            name=dataset_db.name,
            files=dataset_db.files,
            created_at=created_at,
            updated_at=updated_at,
        )

    def _db_prompt_to_proto(self, dataset_db: PromptDataset) -> Any:
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.dataset.v1.prompt_dataset_pb2 import (
            PromptDataset as PromptDatasetProto,
        )

        created_at: Timestamp = Timestamp()
        created_at.FromDatetime(dataset_db.created_at)
        updated_at: Timestamp = Timestamp()
        updated_at.FromDatetime(dataset_db.updated_at)

        return PromptDatasetProto(
            id=dataset_db.id,
            name=dataset_db.name,
            rows=[],
            created_at=created_at,
            updated_at=updated_at,
        )
