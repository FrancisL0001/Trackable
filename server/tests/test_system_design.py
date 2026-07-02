"""Regression tests for the system-design fixes: scale-proof aggregates,
scheduled sync, Canvas pagination, migration/model parity, and reminder prefs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

from app.models import Connection, Item, User
from app.models.enums import ItemKind, ProviderType
from app.schemas.auth import UserCreate
from app.services import dashboard_service, reminder_service, sync_service, user_service

SERVER_DIR = Path(__file__).resolve().parent.parent


def _user(db) -> User:
    return user_service.register(
        db, UserCreate(email="sd@uni.edu", password="password123", full_name="SD")
    )


def _utc(days: float) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


# --- Issue 3: aggregates must be correct beyond any list cap -----------------

def test_dashboard_stats_correct_beyond_500_items(db_session):
    user = _user(db_session)
    db_session.add_all(
        Item(
            owner_id=user.id,
            title=f"item {i}",
            kind=ItemKind.TASK,
            external_id=f"bulk-{i}",
            course="CS 200",
            due_at=_utc(-1) if i < 300 else _utc(2),
        )
        for i in range(600)
    )
    db_session.commit()

    stats = dashboard_service.build_stats(db_session, user.id)
    assert stats["total_open"] == 600
    assert stats["overdue"] == 300
    assert stats["by_course"]["CS 200"] == 600

    buckets = reminder_service.compute_buckets(db_session, user.id)
    # Buckets are explicitly capped for the UI, sorted by due date.
    assert len(buckets["overdue"]) == reminder_service.PER_BUCKET_LIMIT


# --- Issue 2: scheduler refreshes due connections ----------------------------

def test_sync_due_connections_syncs_and_reschedules(db_session):
    user = _user(db_session)
    conn = Connection(owner_id=user.id, provider=ProviderType.CANVAS)
    db_session.add(conn)
    db_session.commit()

    assert sync_service.sync_due_connections(db_session) == 1
    db_session.refresh(conn)
    assert conn.sync_status == "ok"
    assert conn.next_sync_at is not None

    # Not due again yet: nothing to do.
    assert sync_service.sync_due_connections(db_session) == 0


def test_sync_batches_reads_one_query_per_connection(db_session):
    """Upserts must not do one SELECT per item (issue 4)."""
    user = _user(db_session)
    conn = Connection(owner_id=user.id, provider=ProviderType.CANVAS)
    db_session.add(conn)
    db_session.commit()

    from sqlalchemy import event

    statements: list[str] = []
    engine = db_session.get_bind()

    def before_cursor(conn_, cursor, statement, *args):
        if statement.lstrip().upper().startswith("SELECT") and "items" in statement:
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor)
    try:
        result = sync_service.sync_connection(db_session, conn)
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor)

    assert result["created"] > 0
    # One existence query for the whole batch (not one per item).
    assert len(statements) <= 2


# --- Issue 5: Canvas pagination ----------------------------------------------

def test_canvas_follows_pagination_links(monkeypatch):
    from app.integrations.canvas import CanvasIntegration

    base = "https://canvas.example.com"

    def handler(request: httpx.Request) -> httpx.Response:
        path, query = request.url.path, str(request.url.query)
        if path == "/api/v1/courses":
            if "page=2" in query:
                return httpx.Response(200, json=[{"id": 2, "name": "CHEM 33"}])
            return httpx.Response(
                200,
                json=[{"id": 1, "name": "CS 200"}],
                headers={"Link": f'<{base}/api/v1/courses?page=2>; rel="next"'},
            )
        if path == "/api/v1/courses/1/assignments":
            if "page=2" in query:
                return httpx.Response(200, json=[{"id": 12, "name": "PSet 2"}])
            return httpx.Response(
                200,
                json=[{"id": 11, "name": "PSet 1"}],
                headers={
                    "Link": f'<{base}/api/v1/courses/1/assignments?page=2>; rel="next"'
                },
            )
        if path == "/api/v1/courses/2/assignments":
            return httpx.Response(200, json=[{"id": 21, "name": "Lab report"}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "app.integrations.canvas.validate_public_url", lambda url: None
    )
    integration = CanvasIntegration({"token": "tok", "base_url": base}, demo=False)
    integration._transport = httpx.MockTransport(handler)

    items = integration.fetch_items()
    assert {i.title for i in items} == {"PSet 1", "PSet 2", "Lab report"}
    assert {i.course for i in items} == {"CS 200", "CHEM 33"}
    assert integration.partial is False


# --- Issue 9: migrations create the same schema as the models ----------------

def test_alembic_migrations_match_models(tmp_path):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine, inspect

    from app.core.database import Base

    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    cfg = Config(str(SERVER_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(SERVER_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    inspector = inspect(engine)
    migrated_tables = set(inspector.get_table_names()) - {"alembic_version"}
    assert migrated_tables == set(Base.metadata.tables)

    for table_name, table in Base.metadata.tables.items():
        migrated_cols = {c["name"]: c for c in inspector.get_columns(table_name)}
        assert set(migrated_cols) == {c.name for c in table.columns}, table_name
        for col in table.columns:
            assert migrated_cols[col.name]["nullable"] == col.nullable, (
                f"{table_name}.{col.name} nullability"
            )
    engine.dispose()


# --- Issue 11: reminder window preference ------------------------------------

def test_reminder_soon_window_preference(client, auth_headers):
    due_in_5_days = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    client.post(
        "/api/items",
        json={"title": "Essay", "due_at": due_in_5_days},
        headers=auth_headers,
    )

    # Default window (7 days): the essay counts as "soon".
    buckets = client.get("/api/reminders", headers=auth_headers).json()
    assert [i["title"] for i in buckets["soon"]] == ["Essay"]

    # Tighten the window to 3 days: it moves to "upcoming".
    me = client.patch(
        "/api/auth/me", json={"reminder_soon_days": 3}, headers=auth_headers
    )
    assert me.status_code == 200
    assert me.json()["reminder_soon_days"] == 3

    buckets = client.get("/api/reminders", headers=auth_headers).json()
    assert buckets["soon"] == []
    assert [i["title"] for i in buckets["upcoming"]] == ["Essay"]
