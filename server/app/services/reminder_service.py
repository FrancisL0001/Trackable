"""Compute reminder buckets (overdue / today / soon / upcoming) from items.

Each bucket is its own due-date-window query, so buckets stay correct for users
with thousands of items. The "soon" window honours the user's reminder
preference (User.reminder_soon_days). Buckets are truncated only by an explicit
per-bucket limit sized for what the UI actually renders.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models import Item, User
from app.models.enums import ItemStatus

DEFAULT_SOON_DAYS = 7
# The UI shows at most a page's worth of reminders per bucket.
PER_BUCKET_LIMIT = 100


def get_soon_window_days(db: Session, owner_id: int) -> int:
    user = db.get(User, owner_id)
    days = getattr(user, "reminder_soon_days", None) or DEFAULT_SOON_DAYS
    return max(1, min(int(days), 30))


def compute_buckets(
    db: Session,
    owner_id: int,
    now: datetime | None = None,
    per_bucket_limit: int = PER_BUCKET_LIMIT,
) -> dict[str, list[Item]]:
    now = now or utcnow()
    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=0)
    soon_cutoff = now + timedelta(days=get_soon_window_days(db, owner_id))

    def window(*conditions) -> list[Item]:
        stmt = (
            select(Item)
            .where(
                Item.owner_id == owner_id,
                Item.status != ItemStatus.DONE,
                Item.due_at.is_not(None),
                *conditions,
            )
            .order_by(Item.due_at.asc())
            .limit(per_bucket_limit)
        )
        return list(db.scalars(stmt).all())

    return {
        "overdue": window(Item.due_at < now),
        "today": window(Item.due_at >= now, Item.due_at <= end_of_today),
        "soon": window(Item.due_at > end_of_today, Item.due_at <= soon_cutoff),
        "upcoming": window(Item.due_at > soon_cutoff),
    }
