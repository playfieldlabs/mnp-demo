import uuid

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from agent_platform.db.engine import Base


class RewardAgent(Base):
    __tablename__ = "reward_agents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent: Mapped[dict] = mapped_column(JSON, nullable=False)
    force_final_tool_call: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RewardResult(Base):
    __tablename__ = "reward_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    policy_agent_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    latency_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    tool_call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    breakdown: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)


class RewardBreakdown(Base):
    __tablename__ = "reward_breakdowns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    reward_result_id: Mapped[str] = mapped_column(
        String, ForeignKey("reward_results.id", ondelete="CASCADE"), nullable=False
    )
    policy_agent_id: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
