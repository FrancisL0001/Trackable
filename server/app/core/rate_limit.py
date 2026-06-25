"""Rate limiting via SlowAPI, keyed by authenticated user when possible."""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import settings
from app.core.security import decode_access_token


def _key_func(request: Request) -> str:
    """Prefer the authenticated user id; fall back to client IP."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        subject = decode_access_token(auth[7:])
        if subject:
            return f"user:{subject}"
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func, default_limits=[settings.rate_limit_default])
