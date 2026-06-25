"""Compute reminder buckets (overdue / today / soon / upcoming) from items."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.timeutils import ensure_aware, utcnow
from app.models import Item
from app.models.enums import ItemStatus
from app.services import item_service


def _open_items_with_due(db: Session, owner_id: int) -> list[Item]:
    items = item_service.list_items(db, owner_id)
    return [i for i in items if i.due_at is not None and i.status != ItemStatus.DONE]


def compute_buckets(
    db: Session, owner_id: int, now: datetime | None = None
) -> dict[str, list[Item]]:
    now = now or utcnow()
    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=0)
    soon_cutoff = now + timedelta(days=7)

    buckets: dict[str, list[Item]] = {
        "overdue": [],
        "today": [],
        "soon": [],
        "upcoming": [],
    }
    for item in _open_items_with_due(db, owner_id):
        due = ensure_aware(item.due_at)
        if due < now:
            buckets["overdue"].append(item)
        elif due <= end_of_today:
            buckets["today"].append(item)
        elif due <= soon_cutoff:
            buckets["soon"].append(item)
        else:
            buckets["upcoming"].append(item)
    return buckets
