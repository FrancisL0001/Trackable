"""Shared enumerations for the domain model."""
from __future__ import annotations

import enum


class ItemKind(str, enum.Enum):
    ASSIGNMENT = "assignment"
    EVENT = "event"
    MEETING = "meeting"
    TASK = "task"
    JOB = "job"
    EXAM = "exam"
    DEADLINE = "deadline"


class ItemStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class ItemPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProviderType(str, enum.Enum):
    CANVAS = "canvas"
    GOOGLE_CALENDAR = "google_calendar"
    GRADESCOPE = "gradescope"
    ICS = "ics"
    MANUAL = "manual"
