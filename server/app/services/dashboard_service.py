"""Aggregate dashboard statistics straight from the database.

Counts use SQL aggregates rather than loading item rows, so stats stay correct
no matter how many items a user accumulates (no hidden list cap).
"""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.models import Item
from app.models.enums import ItemStatus
from app.services import reminder_service


def build_stats(db: Session, owner_id: int) -> dict:
    now = utcnow()
    end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=0)
    week_ahead = now + timedelta(days=7)
    week_ago = now - timedelta(days=7)

    def count(*conditions) -> int:
        stmt = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id, *conditions)
        )
        return db.scalar(stmt) or 0

    is_open = Item.status != ItemStatus.DONE

    by_course_rows = db.execute(
        select(Item.course, func.count())
        .where(Item.owner_id == owner_id, is_open, Item.course != "")
        .group_by(Item.course)
    ).all()

    return {
        "total_open": count(is_open),
        "overdue": count(is_open, Item.due_at.is_not(None), Item.due_at < now),
        "due_today": count(is_open, Item.due_at >= now, Item.due_at <= end_of_today),
        "due_this_week": count(is_open, Item.due_at >= now, Item.due_at <= week_ahead),
        "completed_this_week": count(
            Item.status == ItemStatus.DONE,
            Item.completed_at.is_not(None),
            Item.completed_at >= week_ago,
        ),
        "by_course": {course: n for course, n in by_course_rows},
    }


def build_dashboard(db: Session, owner_id: int) -> dict:
    buckets = reminder_service.compute_buckets(db, owner_id)
    next_up = (buckets["today"] + buckets["soon"] + buckets["upcoming"])[:5]
    return {
        "stats": build_stats(db, owner_id),
        "reminders": buckets,
        "next_up": next_up,
    }
