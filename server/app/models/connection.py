"""Integration connection model — links a user to an external provider.

Credentials are stored encrypted (Fernet) and never returned to the client.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ProviderType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Connection(Base):
    __tablename__ = "connections"
    __table_args__ = (
        UniqueConstraint("owner_id", "provider", name="uq_connection_provider"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[ProviderType] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    # Encrypted JSON blob of provider-specific secrets (token, url, cookies...).
    encrypted_secrets: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Sync job state machine: idle -> queued -> running -> ok | partial | error.
    sync_status: Mapped[str] = mapped_column(String(20), nullable=False, default="idle")
    last_sync_error: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # When the background scheduler should refresh this connection next.
    next_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync_status: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="connections")  # noqa: F821
