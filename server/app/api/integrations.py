"""Integration (connection) management and sync routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.integrations.registry import SUPPORTED_PROVIDERS
from app.models import User
from app.schemas.connection import ConnectionCreate, ConnectionOut, SyncSummary
from app.services import connection_service, sync_service

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("/providers")
def list_providers() -> dict:
    """Available providers and whether the server is running in demo mode."""
    return {
        "demo_mode": settings.demo_mode,
        "providers": [p.value for p in SUPPORTED_PROVIDERS],
    }


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
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConnectionOut:
    return connection_service.upsert(db, current.id, data)


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


@router.post("/sync", response_model=SyncSummary)
@limiter.limit(settings.rate_limit_sync)
def sync_all(
    request: Request,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SyncSummary:
    return sync_service.sync_all(db, current.id)
