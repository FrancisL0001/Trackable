"""Item CRUD routes (assignments, events, tasks, jobs, ...)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cache import cache
from app.core.database import get_db
from app.models import User
from app.models.enums import ItemKind, ItemStatus, ProviderType
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.services import item_service

router = APIRouter(prefix="/api/items", tags=["items"])


def _invalidate(owner_id: int) -> None:
    cache.invalidate_prefix(f"dashboard:{owner_id}")


@router.get("", response_model=list[ItemOut])
def list_items(
    kind: ItemKind | None = None,
    status_filter: ItemStatus | None = Query(default=None, alias="status"),
    source: ProviderType | None = None,
    course: str | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    search: str | None = None,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ItemOut]:
    return item_service.list_items(
        db,
        current.id,
        kind=kind,
        status=status_filter,
        source=source,
        course=course,
        due_before=due_before,
        due_after=due_after,
        search=search,
    )


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ItemOut:
    item = item_service.create(db, current.id, data)
    _invalidate(current.id)
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ItemOut:
    return item_service.get(db, current.id, item_id)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    data: ItemUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ItemOut:
    item = item_service.update(db, current.id, item_id, data)
    _invalidate(current.id)
    return item


@router.post("/{item_id}/complete", response_model=ItemOut)
def complete_item(
    item_id: int,
    completed: bool = True,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ItemOut:
    item = item_service.set_completed(db, current.id, item_id, completed)
    _invalidate(current.id)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    item_service.delete(db, current.id, item_id)
    _invalidate(current.id)
