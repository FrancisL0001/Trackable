"""Unit tests for service-layer logic without going through HTTP."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import User
from app.models.enums import ItemStatus
from app.schemas.item import ItemCreate
from app.services import (
    dashboard_service,
    item_service,
    reminder_service,
    study_tips,
    user_service,
)
from app.schemas.auth import UserCreate


def _user(db) -> User:
    return user_service.register(
        db, UserCreate(email="svc@uni.edu", password="password123", full_name="Svc")
    )


def _utc(days: float) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def test_reminder_buckets_partition_by_due_date(db_session):
    user = _user(db_session)
    item_service.create(db_session, user.id, ItemCreate(title="overdue", due_at=_utc(-2)))
    item_service.create(db_session, user.id, ItemCreate(title="soon", due_at=_utc(3)))
    item_service.create(db_session, user.id, ItemCreate(title="later", due_at=_utc(20)))

    buckets = reminder_service.compute_buckets(db_session, user.id)
    assert len(buckets["overdue"]) == 1
    assert len(buckets["soon"]) == 1
    assert len(buckets["upcoming"]) == 1


def test_completed_items_excluded_from_reminders(db_session):
    user = _user(db_session)
    item = item_service.create(
        db_session, user.id, ItemCreate(title="done", due_at=_utc(-1))
    )
    item_service.set_completed(db_session, user.id, item.id, True)
    buckets = reminder_service.compute_buckets(db_session, user.id)
    assert buckets["overdue"] == []


def test_dashboard_stats_counts(db_session):
    user = _user(db_session)
    item_service.create(db_session, user.id, ItemCreate(title="a", due_at=_utc(-1), course="CS 200"))
    item_service.create(db_session, user.id, ItemCreate(title="b", due_at=_utc(2), course="CS 200"))
    stats = dashboard_service.build_stats(db_session, user.id)
    assert stats["total_open"] == 2
    assert stats["overdue"] == 1
    assert stats["due_this_week"] == 1
    assert stats["by_course"]["CS 200"] == 2


def test_study_tips_deterministic_with_seed():
    a = study_tips.get_tips(seed=42, count=3)
    b = study_tips.get_tips(seed=42, count=3)
    assert a == b
    assert len(a) == 3


def test_contextual_tips_prioritize_deadlines_when_pressured(db_session):
    user = _user(db_session)
    # Three items due today -> "pressured" state.
    for i in range(3):
        item_service.create(
            db_session,
            user.id,
            ItemCreate(title=f"t{i}", due_at=datetime.now(timezone.utc).replace(hour=23)),
        )
    tips = study_tips.get_contextual_tips(db_session, user.id, count=2)
    assert len(tips) == 2
    assert tips[0]["category"] in {"Prioritization", "Deadlines", "Time management"}
