"""Aggregate dashboard statistics from a user's items."""
from __future__ import annotations

from collections import Counter
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.timeutils import ensure_aware, utcnow
from app.models.enums import ItemStatus
from app.services import item_service, reminder_service


def build_stats(db: Session, owner_id: int) -> dict:
    now = utcnow()
    week_ahead = now + timedelta(days=7)
    week_ago = now - timedelta(days=7)
    items = item_service.list_items(db, owner_id)

    open_items = [i for i in items if i.status != ItemStatus.DONE]
    overdue = due_today = due_week = completed_week = 0
    by_course: Counter[str] = Counter()

    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=0)
    for i in open_items:
        if i.course:
            by_course[i.course] += 1
        due = ensure_aware(i.due_at)
        if due is None:
            continue
        if due < now:
            overdue += 1
        elif due <= end_of_today:
            due_today += 1
        if now <= due <= week_ahead:
            due_week += 1

    for i in items:
        if i.status == ItemStatus.DONE:
            completed = ensure_aware(i.completed_at)
            if completed and completed >= week_ago:
                completed_week += 1

    return {
        "total_open": len(open_items),
        "overdue": overdue,
        "due_today": due_today,
        "due_this_week": due_week,
        "completed_this_week": completed_week,
        "by_course": dict(by_course),
    }


def build_dashboard(db: Session, owner_id: int) -> dict:
    buckets = reminder_service.compute_buckets(db, owner_id)
    next_up = (buckets["today"] + buckets["soon"] + buckets["upcoming"])[:5]
    return {
        "stats": build_stats(db, owner_id),
        "reminders": buckets,
        "next_up": next_up,
    }
