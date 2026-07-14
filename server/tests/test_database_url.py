"""DATABASE_URL normalization for SQLAlchemy + psycopg3."""
from __future__ import annotations

from app.core.config import Settings


def _url(raw: str) -> str:
    return Settings(database_url=raw).sqlalchemy_database_url


def test_sqlite_url_unchanged():
    assert _url("sqlite:///./trackable.db") == "sqlite:///./trackable.db"


def test_heroku_style_postgres_scheme_normalized():
    assert _url("postgres://u:p@host:5432/db") == "postgresql+psycopg://u:p@host:5432/db"


def test_postgresql_scheme_gets_psycopg_driver():
    assert _url("postgresql://u:p@host/db") == "postgresql+psycopg://u:p@host/db"


def test_already_qualified_url_unchanged():
    url = "postgresql+psycopg://u:p@host/db"
    assert _url(url) == url
