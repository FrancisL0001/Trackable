"""Curated study tips with light context-awareness.

Deterministic given a seed so the UI can show a stable "tip of the day" and tests
can assert behavior.
"""
from __future__ import annotations

import random

from sqlalchemy.orm import Session

from app.services import dashboard_service

_TIPS: list[dict[str, str]] = [
    {
        "category": "Time management",
        "title": "Time-box with the Pomodoro technique",
        "body": "Work in focused 25-minute sprints with 5-minute breaks. After four "
        "sprints, take a longer 15–30 minute break. It keeps fatigue low and momentum high.",
    },
    {
        "category": "Prioritization",
        "title": "Eat the frog",
        "body": "Tackle your most important or most dreaded task first thing in the "
        "morning, while your willpower is highest. Everything after feels easier.",
    },
    {
        "category": "Planning",
        "title": "Plan tomorrow, tonight",
        "body": "Spend five minutes each evening picking your top 3 tasks for the next "
        "day. You'll start the morning with direction instead of decision fatigue.",
    },
    {
        "category": "Retention",
        "title": "Use active recall",
        "body": "Close the book and try to write down everything you remember. Testing "
        "yourself beats re-reading for long-term retention.",
    },
    {
        "category": "Retention",
        "title": "Space your repetition",
        "body": "Review material at increasing intervals (1 day, 3 days, 1 week). "
        "Spaced repetition fights the forgetting curve far better than cramming.",
    },
    {
        "category": "Focus",
        "title": "Silence notifications while studying",
        "body": "Each interruption costs ~20 minutes to fully refocus. Put your phone "
        "in another room and use Do Not Disturb during study blocks.",
    },
    {
        "category": "Wellbeing",
        "title": "Protect your sleep before exams",
        "body": "Sleep consolidates memory. A full night's rest the day before a test "
        "usually beats an all-nighter for performance.",
    },
    {
        "category": "Deadlines",
        "title": "Break big assignments into milestones",
        "body": "Split a large project into small, dated sub-tasks. Progress becomes "
        "visible and the deadline stops feeling like a cliff.",
    },
    {
        "category": "Focus",
        "title": "Study in a dedicated spot",
        "body": "Reserve a specific place for studying only. Your brain learns to switch "
        "into focus mode when you sit there.",
    },
    {
        "category": "Wellbeing",
        "title": "Take real breaks",
        "body": "Step away from screens, stretch, or walk. Short movement breaks restore "
        "attention better than scrolling social media.",
    },
]


def all_tips() -> list[dict[str, str]]:
    return list(_TIPS)


def get_tips(seed: int | None = None, count: int = 4) -> list[dict[str, str]]:
    rng = random.Random(seed)
    pool = list(_TIPS)
    rng.shuffle(pool)
    return pool[: min(count, len(pool))]


def get_contextual_tips(db: Session, owner_id: int, count: int = 4) -> list[dict[str, str]]:
    """Surface deadline/prioritization tips first when the user is under pressure."""
    stats = dashboard_service.build_stats(db, owner_id)
    pressured = stats["overdue"] > 0 or stats["due_today"] > 2
    tips = get_tips(seed=owner_id, count=len(_TIPS))
    if pressured:
        priority = {"Prioritization", "Deadlines", "Time management"}
        tips.sort(key=lambda t: 0 if t["category"] in priority else 1)
    return tips[:count]
