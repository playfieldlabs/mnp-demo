import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_platform.db.engine import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    files: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PromptDataset(Base):
    __tablename__ = "prompt_datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    rows: Mapped[list["PromptDatasetRow"]] = relationship(
        "PromptDatasetRow", back_populates="prompt_dataset", cascade="all, delete-orphan"
    )


class PromptDatasetRow(Base):
    __tablename__ = "prompt_dataset_rows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_dataset_id: Mapped[str] = mapped_column(
        String, ForeignKey("prompt_datasets.id", ondelete="CASCADE"), nullable=False
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    reward_agent_id: Mapped[str] = mapped_column(String, nullable=False)
    ground_truths: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    sme_comments: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    prompt_dataset: Mapped["PromptDataset"] = relationship("PromptDataset", back_populates="rows")


class GroundTruth(Base):
    __tablename__ = "ground_truths"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_dataset_row_id: Mapped[str] = mapped_column(
        String, ForeignKey("prompt_dataset_rows.id", ondelete="CASCADE"), nullable=False
    )
    dataset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)


class SMEComment(Base):
    __tablename__ = "sme_comments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_dataset_row_id: Mapped[str] = mapped_column(
        String, ForeignKey("prompt_dataset_rows.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
