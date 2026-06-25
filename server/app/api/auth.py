"""Authentication routes: register, login (JSON + OAuth form), and current user."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut
from app.services import user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> Token:
    return Token(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/register", response_model=Token, status_code=201)
@limiter.limit(settings.rate_limit_auth)
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)) -> Token:
    user = user_service.register(db, data)
    return _token_response(user)


@router.post("/login", response_model=Token)
@limiter.limit(settings.rate_limit_auth)
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = user_service.authenticate(db, data.email, data.password)
    return _token_response(user)


@router.post("/token", response_model=Token, include_in_schema=False)
@limiter.limit(settings.rate_limit_auth)
def login_form(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 password-form login, used by the Swagger UI 'Authorize' button."""
    user = user_service.authenticate(db, form.username, form.password)
    return _token_response(user)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> User:
    return current
