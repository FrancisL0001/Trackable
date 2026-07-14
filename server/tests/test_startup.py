"""Production configuration guard behavior."""
from __future__ import annotations

import pytest

from app.core.config import DEFAULT_SECRET_KEY, Settings
from app.core.startup import check_settings, enforce_settings


def _prod_settings(**overrides) -> Settings:
    base = dict(
        environment="production",
        secret_key="x" * 48,
        encryption_key=_valid_fernet_key(),
        debug=False,
        frontend_origin="https://app.example.com",
        extra_cors_origins="",
        database_url="postgresql://user:pw@host/db",
    )
    base.update(overrides)
    return Settings(**base)


def _valid_fernet_key() -> str:
    from cryptography.fernet import Fernet

    return Fernet.generate_key().decode()


def test_development_never_blocks_even_with_defaults():
    settings = Settings(environment="development", secret_key=DEFAULT_SECRET_KEY)
    errors, _ = check_settings(settings)
    assert errors == []
    enforce_settings(settings)  # must not raise


def test_production_rejects_default_secret():
    settings = _prod_settings(secret_key=DEFAULT_SECRET_KEY)
    errors, _ = check_settings(settings)
    assert any("SECRET_KEY" in e for e in errors)
    with pytest.raises(RuntimeError):
        enforce_settings(settings)


def test_production_rejects_short_secret():
    settings = _prod_settings(secret_key="tooshort")
    errors, _ = check_settings(settings)
    assert any("too short" in e for e in errors)


def test_production_requires_encryption_key():
    settings = _prod_settings(encryption_key=None)
    errors, _ = check_settings(settings)
    assert any("ENCRYPTION_KEY" in e for e in errors)


def test_production_rejects_invalid_encryption_key():
    settings = _prod_settings(encryption_key="not-a-fernet-key")
    errors, _ = check_settings(settings)
    assert any("valid Fernet key" in e for e in errors)


def test_production_rejects_debug_and_localhost_cors():
    settings = _prod_settings(debug=True, frontend_origin="http://localhost:5173")
    errors, _ = check_settings(settings)
    assert any("DEBUG" in e for e in errors)
    assert any("localhost" in e for e in errors)


def test_sqlite_in_production_warns_not_fatal():
    settings = _prod_settings(database_url="sqlite:///./trackable.db")
    errors, warnings = check_settings(settings)
    assert errors == []
    assert any("SQLite" in w for w in warnings)
    enforce_settings(settings)  # warns but does not raise


def test_valid_production_config_passes():
    settings = _prod_settings()
    errors, _ = check_settings(settings)
    assert errors == []
    enforce_settings(settings)


def test_production_rejects_multiple_workers(monkeypatch):
    monkeypatch.setenv("WEB_CONCURRENCY", "4")
    errors, _ = check_settings(_prod_settings())
    assert any("single worker" in e for e in errors)


def test_production_accepts_single_worker(monkeypatch):
    monkeypatch.setenv("WEB_CONCURRENCY", "1")
    errors, _ = check_settings(_prod_settings())
    assert errors == []


def test_development_ignores_worker_count(monkeypatch):
    monkeypatch.setenv("WEB_CONCURRENCY", "4")
    settings = Settings(environment="development")
    errors, _ = check_settings(settings)
    assert errors == []
