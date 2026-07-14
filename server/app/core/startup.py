"""Production configuration guard.

Fails the application closed when it is started in a production-like environment
with insecure or missing configuration. This neutralizes the "predictable default
secret", "encryption key derived from JWT secret", and "dev defaults in production"
classes of issues by refusing to boot rather than running insecurely.

Designed for Railway/Vercel deployments: relies on an explicit ``ENVIRONMENT`` but
also treats a detected Railway environment as production by default.
"""
from __future__ import annotations

import logging
import os

from cryptography.fernet import Fernet

from app.core.config import Settings

logger = logging.getLogger("trackable.startup")

MIN_SECRET_LEN = 32
_LOCAL_HOST_HINTS = ("localhost", "127.0.0.1", "::1", "0.0.0.0")

# Env vars that commonly set the number of server worker processes.
_WORKER_ENV_VARS = ("WEB_CONCURRENCY", "UVICORN_WORKERS", "GUNICORN_WORKERS")


def _configured_workers() -> int | None:
    """Best-effort detection of a multi-worker server configuration."""
    for var in _WORKER_ENV_VARS:
        value = os.getenv(var)
        if value:
            try:
                return int(value)
            except ValueError:
                continue
    return None


def _encryption_key_is_valid(key: str) -> bool:
    try:
        Fernet(key.encode())
        return True
    except (ValueError, TypeError):
        return False


def check_settings(settings: Settings) -> tuple[list[str], list[str]]:
    """Return (fatal_errors, warnings) for the given settings.

    Errors are only populated for production-like environments; warnings may be
    emitted in any environment.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not settings.is_production:
        # Non-production: never block startup, but still surface gentle hints.
        if settings.uses_default_secret:
            warnings.append("Using the default SECRET_KEY (fine for local/demo only).")
        return errors, warnings

    # --- Production checks (fail closed) ---
    if settings.uses_default_secret:
        errors.append(
            "SECRET_KEY is still the insecure default. Set a strong, unique value."
        )
    elif len(settings.secret_key) < MIN_SECRET_LEN:
        errors.append(
            f"SECRET_KEY is too short (< {MIN_SECRET_LEN} chars). Use a high-entropy value."
        )

    if not settings.encryption_key:
        errors.append(
            "ENCRYPTION_KEY must be set in production (separate from SECRET_KEY). "
            "Generate one with: python -c \"from cryptography.fernet import Fernet; "
            'print(Fernet.generate_key().decode())"'
        )
    elif not _encryption_key_is_valid(settings.encryption_key):
        errors.append(
            "ENCRYPTION_KEY is not a valid Fernet key (urlsafe base64, 32 bytes)."
        )

    if settings.debug:
        errors.append("DEBUG must be false in production.")

    origins = settings.cors_origins
    if not origins:
        errors.append("No CORS origins configured. Set FRONTEND_ORIGIN to your site URL.")
    for origin in origins:
        if origin == "*":
            errors.append("CORS origin '*' is not allowed in production.")
        elif any(hint in origin for hint in _LOCAL_HOST_HINTS):
            errors.append(f"CORS origin '{origin}' points at localhost; set your real site URL.")

    # The in-process cache, rate limiter, and sync scheduler all assume exactly
    # one worker process. Multiple workers would mean inconsistent rate limits,
    # stale dashboard caches, and duplicate scheduled syncs — fail closed until
    # those are backed by Redis / a real queue.
    workers = _configured_workers()
    if workers is not None and workers > 1:
        errors.append(
            f"This build requires a single worker process (got {workers}). "
            "In-memory cache/rate-limiting/sync-scheduling are per-process; "
            "set WEB_CONCURRENCY=1 or move to Redis-backed infrastructure first."
        )

    # SQLite is fine for small scale but is easy to mishandle / non-persistent on
    # ephemeral hosts. Warn rather than block (a Railway volume can make it valid).
    if settings.database_url.startswith("sqlite"):
        warnings.append(
            "DATABASE_URL uses SQLite. On Railway this is ephemeral unless backed by a "
            "volume; prefer a managed Postgres DATABASE_URL for production."
        )

    return errors, warnings


def enforce_settings(settings: Settings) -> None:
    """Log warnings and raise RuntimeError on fatal production misconfiguration."""
    errors, warnings = check_settings(settings)
    for w in warnings:
        logger.warning("Config warning: %s", w)
    if errors:
        joined = "\n  - ".join(errors)
        raise RuntimeError(
            "Refusing to start: insecure/incomplete production configuration:\n  - "
            + joined
        )
