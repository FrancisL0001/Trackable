"""Deterministic synthetic data for demo-mode providers.

Dates are generated relative to "now" so the demo always looks current — some items
overdue, some due today, some upcoming.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.core.timeutils import utcnow
from app.integrations.base import NormalizedItem
from app.models.enums import ItemKind, ItemPriority, ProviderType


def _at(days: float, hour: int = 23, minute: int = 59) -> datetime:
    base = utcnow() + timedelta(days=days)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def canvas_items() -> list[NormalizedItem]:
    return [
        NormalizedItem(
            external_id="canvas-1",
            title="Problem Set 4: Dynamic Programming",
            kind=ItemKind.ASSIGNMENT,
            course="CS 200",
            description="Submit your solutions as a single PDF on Canvas.",
            url="https://canvas.instructure.com/courses/1/assignments/1",
            due_at=_at(-1),
            priority=ItemPriority.HIGH,
        ),
        NormalizedItem(
            external_id="canvas-2",
            title="Reading Response: Chapter 7",
            kind=ItemKind.ASSIGNMENT,
            course="HIST 110",
            description="300-word reflection on the assigned reading.",
            url="https://canvas.instructure.com/courses/2/assignments/2",
            due_at=_at(0, hour=17),
            priority=ItemPriority.MEDIUM,
        ),
        NormalizedItem(
            external_id="canvas-3",
            title="Lab 3 Report",
            kind=ItemKind.ASSIGNMENT,
            course="PHYS 070",
            description="Write up your pendulum experiment results.",
            url="https://canvas.instructure.com/courses/3/assignments/3",
            due_at=_at(3),
            priority=ItemPriority.MEDIUM,
        ),
        NormalizedItem(
            external_id="canvas-4",
            title="Midterm Exam",
            kind=ItemKind.EXAM,
            course="CS 200",
            description="Covers chapters 1–6. In-person, closed book.",
            location="Sayles Hall 104",
            start_at=_at(9, hour=10, minute=0),
            due_at=_at(9, hour=12, minute=0),
            priority=ItemPriority.HIGH,
        ),
    ]


def gradescope_items() -> list[NormalizedItem]:
    return [
        NormalizedItem(
            external_id="gs-1",
            title="Homework 5 (autograded)",
            kind=ItemKind.ASSIGNMENT,
            course="CS 200",
            description="Gradescope autograder closes at the deadline.",
            url="https://www.gradescope.com/courses/1/assignments/1",
            due_at=_at(2, hour=22),
            priority=ItemPriority.HIGH,
        ),
        NormalizedItem(
            external_id="gs-2",
            title="Written Assignment 3",
            kind=ItemKind.ASSIGNMENT,
            course="MATH 100",
            description="Upload your handwritten solutions and tag each question.",
            url="https://www.gradescope.com/courses/2/assignments/2",
            due_at=_at(5, hour=20),
            priority=ItemPriority.MEDIUM,
        ),
    ]


def google_calendar_items() -> list[NormalizedItem]:
    return [
        NormalizedItem(
            external_id="gcal-1",
            title="Study group — Algorithms",
            kind=ItemKind.MEETING,
            description="Weekly study group with the cohort.",
            location="SciLi Room 220",
            start_at=_at(1, hour=18, minute=0),
            due_at=_at(1, hour=19, minute=30),
            priority=ItemPriority.LOW,
        ),
        NormalizedItem(
            external_id="gcal-2",
            title="Advisor meeting",
            kind=ItemKind.MEETING,
            description="Course selection for next semester.",
            location="Office hours, CIT 3rd floor",
            start_at=_at(4, hour=14, minute=0),
            due_at=_at(4, hour=14, minute=30),
            priority=ItemPriority.MEDIUM,
        ),
        NormalizedItem(
            external_id="gcal-3",
            title="Career fair",
            kind=ItemKind.EVENT,
            description="Bring printed resumes. Tech companies in the main hall.",
            location="Student Union",
            start_at=_at(6, hour=11, minute=0),
            due_at=_at(6, hour=15, minute=0),
            priority=ItemPriority.MEDIUM,
        ),
    ]


def ics_items() -> list[NormalizedItem]:
    return [
        NormalizedItem(
            external_id="ics-1",
            title="Final Project Proposal Due",
            kind=ItemKind.DEADLINE,
            course="CS 200",
            description="Imported from the course website calendar feed.",
            due_at=_at(8, hour=23, minute=59),
            priority=ItemPriority.HIGH,
        ),
        NormalizedItem(
            external_id="ics-2",
            title="Internship application deadline — Acme Corp",
            kind=ItemKind.JOB,
            description="Submit resume and cover letter through the portal.",
            url="https://example.com/careers/acme",
            due_at=_at(11, hour=23, minute=59),
            priority=ItemPriority.HIGH,
        ),
    ]


def web_page_items() -> list[NormalizedItem]:
    return [
        NormalizedItem(
            external_id="web-demo-1",
            title="Homework 2: Regular Languages",
            kind=ItemKind.ASSIGNMENT,
            course="CS 0220",
            description="Extracted from the course website assignments page.",
            url="https://example.edu/cs0220/assignments",
            due_at=_at(4),
            priority=ItemPriority.MEDIUM,
        ),
        NormalizedItem(
            external_id="web-demo-2",
            title="Project 1 checkpoint",
            kind=ItemKind.DEADLINE,
            course="CS 0220",
            description="Extracted from the course website assignments page.",
            url="https://example.edu/cs0220/projects",
            due_at=_at(9),
            priority=ItemPriority.HIGH,
        ),
    ]


DEMO_BY_PROVIDER = {
    ProviderType.CANVAS: canvas_items,
    ProviderType.GRADESCOPE: gradescope_items,
    ProviderType.GOOGLE_CALENDAR: google_calendar_items,
    ProviderType.ICS: ics_items,
    ProviderType.WEB_PAGE: web_page_items,
}
