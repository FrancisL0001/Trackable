"""Datetime normalization helpers.

SQLite does not persist timezone info, so datetimes read back are naive. We treat
all naive datetimes as UTC to keep comparisons correct and consistent.
"""
from __future__ import annotations

from datetime import datetime, timezone


def ensure_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
