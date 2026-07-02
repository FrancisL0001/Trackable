"""Integration (connection) management and sync routes.

Sync endpoints only *enqueue* work; the actual provider fetch runs as a
background task so API requests stay fast. Clients poll ``GET /connections``
(``sync_status`` per connection) to observe progress.
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.integrations.registry import connectable_providers
from app.models import User
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionOut,
    ProviderInfo,
    ProvidersOut,
    SyncQueued,
)
from app.services import connection_service, sync_service

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/providers", response_model=ProvidersOut)
def list_providers() -> ProvidersOut:
    """Connectable providers with capability metadata, plus server sync mode."""
    return ProvidersOut(
        demo_mode=settings.demo_mode,
        sync_interval_minutes=settings.sync_interval_minutes,
        providers=[
            ProviderInfo(
                id=c.provider,
                label=c.label,
                description=c.description,
                live_supported=c.live_supported,
                note=c.note,
            )
            for c in connectable_providers()
        ],
    )


@router.get("/connections", response_model=list[ConnectionOut])
def list_connections(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[ConnectionOut]:
    return connection_service.list_connections(db, current.id)


@router.post(
    "/connections", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED
)
def create_connection(
    data: ConnectionCreate,
    background: BackgroundTasks,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConnectionOut:
    conn = connection_service.upsert(db, current.id, data)
    # First sync starts immediately so a new connection is useful right away.
    queued = sync_service.queue_connections(db, current.id, [conn.id])
    if queued:
        background.add_task(sync_service.run_sync_job, current.id, [conn.id])
    return conn


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    connection_service.delete(db, current.id, connection_id)


@router.post("/connections/{connection_id}/active", response_model=ConnectionOut)
def toggle_connection(
    connection_id: int,
    active: bool,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConnectionOut:
    return connection_service.set_active(db, current.id, connection_id, active)


@router.post("/sync", response_model=SyncQueued, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.rate_limit_sync)
def sync_all(
    request: Request,
    background: BackgroundTasks,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SyncQueued:
    queued = sync_service.queue_connections(db, current.id)
    if queued:
        background.add_task(
            sync_service.run_sync_job, current.id, [c.id for c in queued]
        )
        detail = f"Sync started for {len(queued)} connection(s)."
    else:
        detail = "Nothing to sync."
    return SyncQueued(
        queued=[ConnectionOut.model_validate(c) for c in queued], detail=detail
    )
