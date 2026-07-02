"""Database engine, session factory, and FastAPI dependency."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _engine_kwargs(url: str) -> dict:
    # check_same_thread is a SQLite-specific requirement for multi-threaded servers.
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    # Postgres (or other server DBs): verify connections and recycle them to survive
    # idle drops on managed hosts like Railway.
    return {"pool_pre_ping": True, "pool_recycle": 1800}


_db_url = settings.sqlalchemy_database_url
engine = create_engine(_db_url, **_engine_kwargs(_db_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, ensuring it is always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Ensure the schema exists.

    Local/dev/test: bootstrap with create_all for zero-setup runs.
    Production: the schema is owned by Alembic (`alembic upgrade head`, run by
    the container entrypoint); refuse to serve if migrations haven't been applied
    rather than silently creating an unversioned schema.
    """
    # Import models so they are registered on Base.metadata.
    from app import models  # noqa: F401

    if not settings.is_production:
        Base.metadata.create_all(bind=engine)
        return

    inspector = inspect(engine)
    missing = [t for t in Base.metadata.tables if not inspector.has_table(t)]
    if missing:
        raise RuntimeError(
            "Database schema is missing tables "
            f"{missing}: run `alembic upgrade head` before starting the server."
        )
