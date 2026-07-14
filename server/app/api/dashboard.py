"""Dashboard, reminders, and study-tips routes (read-heavy, cached)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.cache import cache
from app.core.database import get_db
from app.models import User
from app.schemas.misc import Dashboard, ReminderBuckets, StudyTip
from app.services import dashboard_service, reminder_service, study_tips

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=Dashboard)
def get_dashboard(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dashboard:
    key = f"dashboard:{current.id}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    data = dashboard_service.build_dashboard(db, current.id)
    result = Dashboard.model_validate(data)
    cache.set(key, result)
    return result


@router.get("/reminders", response_model=ReminderBuckets)
def get_reminders(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ReminderBuckets:
    buckets = reminder_service.compute_buckets(db, current.id)
    return ReminderBuckets.model_validate(buckets)


@router.get("/study-tips", response_model=list[StudyTip])
def get_study_tips(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[StudyTip]:
    return [StudyTip(**t) for t in study_tips.get_contextual_tips(db, current.id)]
