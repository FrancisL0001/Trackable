"""Unified Item model.

Assignments, events, meetings, tasks, jobs, exams, and deadlines are all stored as
one polymorphic row discriminated by ``kind``. ``source`` + ``external_id`` track
provenance and make sync idempotent.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ItemKind, ItemPriority, ItemStatus, ProviderType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        # Idempotent sync: one row per (user, source, external id).
        UniqueConstraint("owner_id", "source", "external_id", name="uq_item_source"),
        Index("ix_items_owner_due", "owner_id", "due_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    kind: Mapped[ItemKind] = mapped_column(String(20), default=ItemKind.TASK, nullable=False)
    status: Mapped[ItemStatus] = mapped_column(
        String(20), default=ItemStatus.TODO, nullable=False
    )
    priority: Mapped[ItemPriority] = mapped_column(
        String(10), default=ItemPriority.MEDIUM, nullable=False
    )

    course: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    url: Mapped[str] = mapped_column(String(1000), nullable=False, default="")

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Provenance for sync de-duplication.
    source: Mapped[ProviderType] = mapped_column(
        String(20), default=ProviderType.MANUAL, nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    owner: Mapped["User"] = relationship(back_populates="items")  # noqa: F821
