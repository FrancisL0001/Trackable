"""Schemas for dashboards, reminders, and study tips."""
from __future__ import annotations

from pydantic import BaseModel

from app.schemas.item import ItemOut


class ReminderBuckets(BaseModel):
    overdue: list[ItemOut]
    today: list[ItemOut]
    soon: list[ItemOut]  # next 7 days, excluding today
    upcoming: list[ItemOut]  # beyond 7 days


class DashboardStats(BaseModel):
    total_open: int
    overdue: int
    due_today: int
    due_this_week: int
    completed_this_week: int
    by_course: dict[str, int]


class Dashboard(BaseModel):
    stats: DashboardStats
    reminders: ReminderBuckets
    next_up: list[ItemOut]


class StudyTip(BaseModel):
    title: str
    body: str
    category: str
