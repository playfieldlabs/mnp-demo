import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_platform.db.engine import Base


class PolicyAgent(Base):
    __tablename__ = "policy_agents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    policy_tool: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    data_source_ids: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    external_source_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    update_schedule: Mapped[str] = mapped_column(String, nullable=False, default="")
    last_updated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    runs: Mapped[list["PolicyRun"]] = relationship(
        "PolicyRun", back_populates="policy_agent", cascade="all, delete-orphan"
    )


class PolicyRun(Base):
    __tablename__ = "policy_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_agent_id: Mapped[str] = mapped_column(
        String, ForeignKey("policy_agents.id", ondelete="CASCADE"), nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    policy_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    policy_agent: Mapped["PolicyAgent"] = relationship("PolicyAgent", back_populates="runs")


class PolicyTool(Base):
    __tablename__ = "policy_tools"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_agent_id: Mapped[str] = mapped_column(
        String, ForeignKey("policy_agents.id", ondelete="CASCADE"), nullable=False
    )
    tool: Mapped[dict] = mapped_column(JSON, nullable=False)
    policy_content: Mapped[str] = mapped_column(Text, nullable=False)
