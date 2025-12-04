from typing import Any

from agent_platform.common.v1.types_pb2 import PaginationResponse
from agent_platform.db.engine import AsyncSessionLocal
from agent_platform.db.models.trajectory import Trajectory
from agent_platform.db.repository.trajectory import TrajectoryRepository
from agent_platform.service.v1.trajectory_service_connect import (
    TrajectoryService,
)
from agent_platform.service.v1.trajectory_service_pb2 import (
    GetTrajectoryResponse,
    ListTrajectoriesResponse,
)


class TrajectoryServiceImpl(TrajectoryService):
    def __init__(self) -> None:
        pass

    async def get_trajectory(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: TrajectoryRepository = TrajectoryRepository(session)
            trajectory: Trajectory | None = await repo.get_by_id(request.trajectory_id)
            if not trajectory:
                raise ValueError(f"Trajectory {request.trajectory_id} not found")
            return GetTrajectoryResponse(trajectory=self._db_to_proto(trajectory))

    async def list_trajectories(self, request, ctx):
        async with AsyncSessionLocal() as session:
            repo: TrajectoryRepository = TrajectoryRepository(session)
            page_size: int = (
                request.pagination.page_size
                if request.pagination and request.pagination.page_size > 0
                else 100
            )
            trajectories: list[Trajectory] = await repo.get_all(limit=page_size, offset=0)
            return ListTrajectoriesResponse(
                trajectories=[self._db_to_proto(t) for t in trajectories],
                pagination=PaginationResponse(
                    next_page_token="",
                    total_count=len(trajectories),
                ),
            )

    def _db_to_proto(self, trajectory_db: Trajectory) -> Any:
        from google.protobuf.timestamp_pb2 import Timestamp

        from agent_platform.trajectory.v1.trajectory_pb2 import (
            Trajectory as TrajectoryProto,
        )

        created_at: Timestamp = Timestamp()
        created_at.FromDatetime(trajectory_db.created_at)

        return TrajectoryProto(
            id=trajectory_db.id,
            agent_id=trajectory_db.agent_id,
            agent_run=trajectory_db.agent_run,
            reward=trajectory_db.reward,
            annotation=trajectory_db.annotation,
            created_at=created_at,
        )
