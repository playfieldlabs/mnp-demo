import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agent_platform.db.engine import Base


class Trajectory(Base):
    __tablename__ = "trajectories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, nullable=False)
    agent_run: Mapped[dict] = mapped_column(JSON, nullable=False)
    reward: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    annotation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class TrajectoryAnnotation(Base):
    __tablename__ = "trajectory_annotations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trajectory_id: Mapped[str] = mapped_column(
        String, ForeignKey("trajectories.id", ondelete="CASCADE"), nullable=False
    )
    annotator_id: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_annotations: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    annotated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class StepAnnotation(Base):
    __tablename__ = "step_annotations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trajectory_annotation_id: Mapped[str] = mapped_column(
        String, ForeignKey("trajectory_annotations.id", ondelete="CASCADE"), nullable=False
    )
    block_id: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
