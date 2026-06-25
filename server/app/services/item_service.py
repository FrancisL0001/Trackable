"""Item CRUD and querying, always scoped to an owner."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models import Item
from app.models.enums import ItemKind, ItemStatus, ProviderType
from app.schemas.item import ItemCreate, ItemUpdate


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create(db: Session, owner_id: int, data: ItemCreate) -> Item:
    item = Item(
        owner_id=owner_id,
        source=ProviderType.MANUAL,
        # Manual items need a unique external_id so several can coexist under the
        # (owner, source, external_id) uniqueness used for sync de-duplication.
        external_id=f"manual-{uuid4().hex}",
        **data.model_dump(),
    )
    if item.status == ItemStatus.DONE and item.completed_at is None:
        item.completed_at = _utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get(db: Session, owner_id: int, item_id: int) -> Item:
    item = db.get(Item, item_id)
    if item is None or item.owner_id != owner_id:
        raise NotFoundError("Item not found.")
    return item


def list_items(
    db: Session,
    owner_id: int,
    *,
    kind: ItemKind | None = None,
    status: ItemStatus | None = None,
    source: ProviderType | None = None,
    course: str | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    search: str | None = None,
    limit: int = 500,
) -> list[Item]:
    conditions = [Item.owner_id == owner_id]
    if kind is not None:
        conditions.append(Item.kind == kind)
    if status is not None:
        conditions.append(Item.status == status)
    if source is not None:
        conditions.append(Item.source == source)
    if course:
        conditions.append(Item.course == course)
    if due_before is not None:
        conditions.append(Item.due_at <= due_before)
    if due_after is not None:
        conditions.append(Item.due_at >= due_after)
    if search:
        like = f"%{search.lower()}%"
        conditions.append(Item.title.ilike(like))

    stmt = (
        select(Item)
        .where(and_(*conditions))
        # NULLs (no due date) sort last; otherwise ascending by due date.
        .order_by(Item.due_at.is_(None), Item.due_at.asc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def update(db: Session, owner_id: int, item_id: int, data: ItemUpdate) -> Item:
    item = get(db, owner_id, item_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(item, field, value)
    # Keep completed_at consistent with status transitions.
    if "status" in changes:
        if item.status == ItemStatus.DONE and item.completed_at is None:
            item.completed_at = _utcnow()
        elif item.status != ItemStatus.DONE:
            item.completed_at = None
    db.commit()
    db.refresh(item)
    return item


def set_completed(db: Session, owner_id: int, item_id: int, completed: bool) -> Item:
    item = get(db, owner_id, item_id)
    if completed:
        item.status = ItemStatus.DONE
        item.completed_at = item.completed_at or _utcnow()
    else:
        item.status = ItemStatus.TODO
        item.completed_at = None
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, owner_id: int, item_id: int) -> None:
    item = get(db, owner_id, item_id)
    db.delete(item)
    db.commit()
