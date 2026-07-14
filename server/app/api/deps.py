"""Shared API dependencies: DB session and current-user resolution."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise _CREDENTIALS_EXC
    subject = decode_access_token(token)
    if subject is None:
        raise _CREDENTIALS_EXC
    try:
        user = user_service.get_by_id(db, int(subject))
    except (TypeError, ValueError):
        raise _CREDENTIALS_EXC
    if user is None:
        raise _CREDENTIALS_EXC
    return user
