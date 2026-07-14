"""User registration and authentication logic (no transport concerns)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AuthError, ConflictError
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.auth import UserCreate, UserUpdate


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def register(db: Session, data: UserCreate) -> User:
    if get_by_email(db, data.email):
        raise ConflictError("An account with this email already exists.")
    user = User(
        email=data.email.lower(),
        full_name=data.full_name.strip(),
        timezone=data.timezone or "UTC",
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "full_name" in changes:
        changes["full_name"] = changes["full_name"].strip()
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password.")
    return user
