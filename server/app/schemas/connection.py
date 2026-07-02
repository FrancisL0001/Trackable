"""Connection (integration) schemas. Secrets are write-only and never returned."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProviderType


class ConnectionCreate(BaseModel):
    provider: ProviderType
    display_name: str = Field(default="", max_length=200)
    # Provider-specific secrets (e.g. {"token": "...", "base_url": "..."}).
    # Optional because demo-mode connections require no real credentials.
    secrets: dict[str, str] = Field(default_factory=dict)


class ConnectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: ProviderType
    is_active: bool
    display_name: str
    sync_status: str
    last_sync_error: str
    last_synced_at: datetime | None
    next_sync_at: datetime | None
    last_sync_status: str
    created_at: datetime


class ProviderInfo(BaseModel):
    """Capability metadata for one connectable provider."""

    id: ProviderType
    label: str
    description: str
    live_supported: bool
    note: str


class ProvidersOut(BaseModel):
    demo_mode: bool
    sync_interval_minutes: int
    providers: list[ProviderInfo]


class SyncQueued(BaseModel):
    """Response to a sync request: work is queued, poll connections for status."""

    queued: list[ConnectionOut]
    detail: str
