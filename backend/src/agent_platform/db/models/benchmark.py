import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from agent_platform.db.engine import Base


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, nullable=False)
    prompt_dataset_id: Mapped[str] = mapped_column(String, nullable=False)
    rows: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    final_reward: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class BenchmarkRunRow(Base):
    __tablename__ = "benchmark_run_rows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    benchmark_run_id: Mapped[str] = mapped_column(
        String, ForeignKey("benchmark_runs.id", ondelete="CASCADE"), nullable=False
    )
    prompt_dataset_row_id: Mapped[str] = mapped_column(String, nullable=False)
    reward: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    agent_run_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    sme_comments: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[int] = mapped_column(Integer, nullable=False)


class BenchmarkConfig(Base):
    __tablename__ = "benchmark_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    benchmark_run_id: Mapped[str] = mapped_column(
        String, ForeignKey("benchmark_runs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    runs_per_prompt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_parallel_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    save_trajectories: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
