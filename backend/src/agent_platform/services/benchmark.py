from typing import Any

from agent_platform.common.v1.types_pb2 import PaginationResponse
from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.benchmark import BenchmarkRun
from agent_platform.db.repository.benchmark import BenchmarkRunRepository
from agent_platform.service.v1.benchmark_service_connect import (
    BenchmarkService,
)
from agent_platform.service.v1.benchmark_service_pb2 import (
    CreateBenchmarkRunResponse,
    GetBenchmarkRunResponse,
    ListBenchmarkRunsResponse,
)


class BenchmarkServiceImpl(BenchmarkService):
    def __init__(self) -> None:
        pass

    async def create_benchmark_run(self, request, ctx):
        import uuid
        from datetime import datetime

        async with AsyncSessionLocal() as session:
            repo: BenchmarkRunRepository = BenchmarkRunRepository(session)
            run: BenchmarkRun = await repo.create(
                id=str(uuid.uuid4()),
                agent_id=request.agent_id,
                prompt_dataset_id=request.prompt_dataset_id,
                rows=[],
                status=0,
                started_at=datetime.utcnow(),
                config=dict(request.config) if request.config else None,
            )
            await session.commit()
            return CreateBenchmarkRunResponse(benchmark_run=self._db_to_proto(run))

    async def get_benchmark_run(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: BenchmarkRunRepository = BenchmarkRunRepository(session)
            run: BenchmarkRun | None = await repo.get_by_id(request.benchmark_run_id)
            if not run:
                raise ValueError(f"Benchmark run {request.benchmark_run_id} not found")
            return GetBenchmarkRunResponse(benchmark_run=self._db_to_proto(run))

    async def list_benchmark_runs(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: BenchmarkRunRepository = BenchmarkRunRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            runs: list[BenchmarkRun] = await repo.get_by_agent_id(
                request.agent_id, limit=page_size, offset=0
            )
            return ListBenchmarkRunsResponse(
                benchmark_runs=[self._db_to_proto(r) for r in runs],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(runs),
                ),
            )

    def _db_to_proto(self, run_db: BenchmarkRun) -> Any:
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.benchmark.v1.benchmark_pb2 import (
            BenchmarkRun as BenchmarkRunProto,
        )

        started_at: Timestamp = Timestamp()
        started_at.FromDatetime(run_db.started_at)
        finished_at: Timestamp | None = None
        if run_db.finished_at:
            finished_at = Timestamp()
            finished_at.FromDatetime(run_db.finished_at)

        return BenchmarkRunProto(
            id=run_db.id,
            agent_id=run_db.agent_id,
            prompt_dataset_id=run_db.prompt_dataset_id,
            rows=run_db.rows,
            final_reward=run_db.final_reward,
            status=run_db.status,
            started_at=started_at,
            finished_at=finished_at,
            config=run_db.config,
        )
