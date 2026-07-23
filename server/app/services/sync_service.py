"""Pull items from connected providers and upsert them idempotently.

Sync runs in the background (request handlers only enqueue) and is tracked per
connection via ``Connection.sync_status``: idle -> queued -> running -> ok |
partial | error. A periodic scheduler re-syncs active connections whose
``next_sync_at`` has passed, so data stays fresh without manual syncs.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import database
from app.core.cache import cache
from app.core.config import settings
from app.core.errors import IntegrationError
from app.core.timeutils import ensure_aware, utcnow
from app.core.urls import sanitize_web_url
from app.integrations.base import NormalizedItem
from app.integrations.registry import build_integration
from app.models import Connection, Item
from app.models.enums import ItemStatus
from app.services import connection_service

logger = logging.getLogger("trackable.sync")

# Fields owned by the provider and refreshed on every sync — unless the user has
# manually edited them (tracked in Item.user_edited_fields).
PROVIDER_OWNED_FIELDS = (
    "title",
    "description",
    "kind",
    "course",
    "location",
    "url",
    "start_at",
    "due_at",
)

# A connection stuck in queued/running longer than this is assumed to have died
# (e.g. process restart mid-sync) and may be re-queued.
STALE_SYNC = timedelta(minutes=10)


def _apply_provider_fields(item: Item, n: NormalizedItem) -> None:
    """Refresh provider-owned fields, preserving user-edited ones."""
    edited = set(item.user_edited_fields or [])
    values = {
        "title": n.title,
        "description": n.description,
        "kind": n.kind,
        "course": n.course,
        "location": n.location,
        "url": sanitize_web_url(n.url),  # drop unsafe URL schemes from upstream data
        "start_at": n.start_at,
        "due_at": n.due_at,
    }
    for field, value in values.items():
        if field not in edited:
            setattr(item, field, value)


def _upsert_batch(
    db: Session, connection: Connection, normalized: list[NormalizedItem]
) -> tuple[int, int]:
    """Insert/update all items for one connection with a single existence query.

    Scoped by connection (not just provider) so several feeds of the same
    provider — e.g. one ICS calendar per course — never overwrite each other.
    """
    existing_by_external_id: dict[str, Item] = {
        item.external_id: item
        for item in db.scalars(
            select(Item).where(
                Item.owner_id == connection.owner_id,
                Item.connection_id == connection.id,
            )
        )
    }
    created = updated = 0
    seen: set[str] = set()
    for n in normalized:
        if n.external_id in seen:  # guard against duplicate ids within one feed
            continue
        seen.add(n.external_id)
        item = existing_by_external_id.get(n.external_id)
        if item is not None:
            _apply_provider_fields(item, n)
            updated += 1
            continue
        item = Item(
            owner_id=connection.owner_id,
            source=connection.provider,
            connection_id=connection.id,
            external_id=n.external_id,
            status=ItemStatus.TODO,
            priority=n.priority,
        )
        _apply_provider_fields(item, n)
        db.add(item)
        created += 1
    return created, updated


def _schedule_next(connection: Connection) -> None:
    connection.next_sync_at = utcnow() + timedelta(
        minutes=settings.sync_interval_minutes
    )


def sync_connection(db: Session, connection: Connection) -> dict:
    """Fetch + upsert one connection, updating its sync state. Commits."""
    owner_id = connection.owner_id
    connection.sync_status = "running"
    db.commit()

    created = updated = total = 0
    try:
        secrets = connection_service.decrypt_secrets(connection)
        integration = build_integration(connection.provider, secrets)
        # Content-hash change detection (web_page): skip extraction on no change.
        integration.previous_hash = connection.last_content_hash
        items = integration.fetch_items()
        if integration.content_hash:
            connection.last_content_hash = integration.content_hash
        if integration.unchanged:
            connection.sync_status = "ok"
            connection.last_sync_error = ""
            connection.last_sync_status = "ok: source unchanged, items kept"
            connection.last_synced_at = utcnow()
            _schedule_next(connection)
            db.commit()
            return {
                "provider": connection.provider,
                "created": 0,
                "updated": 0,
                "total": 0,
                "status": "ok",
            }
        created, updated = _upsert_batch(db, connection, items)
        total = len(items)
        if integration.partial:
            connection.sync_status = "partial"
            connection.last_sync_error = integration.partial_reason[:500]
            connection.last_sync_status = (
                f"partial: {total} items ({integration.partial_reason})"[:500]
            )
        else:
            connection.sync_status = "ok"
            connection.last_sync_error = ""
            connection.last_sync_status = f"ok: {total} items"
    except IntegrationError as exc:
        db.rollback()
        connection.sync_status = "error"
        connection.last_sync_error = exc.message[:500]
        connection.last_sync_status = f"error: {exc.message}"[:500]
    connection.last_synced_at = utcnow()
    _schedule_next(connection)
    db.commit()
    cache.invalidate_prefix(f"dashboard:{owner_id}")
    return {
        "provider": connection.provider,
        "created": created,
        "updated": updated,
        "total": total,
        "status": connection.sync_status,
    }


def _is_stale(connection: Connection) -> bool:
    last = ensure_aware(connection.last_synced_at)
    return last is None or utcnow() - last > STALE_SYNC


def queue_connections(
    db: Session, owner_id: int, connection_ids: list[int] | None = None
) -> list[Connection]:
    """Mark active connections as queued and return them.

    Connections already queued/running are skipped (unless stale) so repeated
    sync clicks don't pile up duplicate work.
    """
    queued: list[Connection] = []
    for conn in connection_service.list_connections(db, owner_id):
        if not conn.is_active:
            continue
        if connection_ids is not None and conn.id not in connection_ids:
            continue
        if conn.sync_status in ("queued", "running") and not _is_stale(conn):
            continue
        conn.sync_status = "queued"
        queued.append(conn)
    db.commit()
    return queued


def run_sync_job(owner_id: int, connection_ids: list[int]) -> None:
    """Background entry point: sync the given connections in a fresh session."""
    db = database.SessionLocal()
    try:
        for cid in connection_ids:
            conn = db.get(Connection, cid)
            if conn is None or conn.owner_id != owner_id or not conn.is_active:
                continue
            try:
                sync_connection(db, conn)
            except Exception:  # keep one bad connection from killing the batch
                logger.exception("Sync failed for connection %s", cid)
                db.rollback()
    finally:
        db.close()


def sync_due_connections(db: Session, now=None) -> int:
    """Sync every active connection whose next_sync_at has passed (scheduler)."""
    now = now or utcnow()
    synced = 0
    for conn in db.scalars(select(Connection).where(Connection.is_active.is_(True))):
        next_at = ensure_aware(conn.next_sync_at)
        if next_at is not None and next_at > now:
            continue
        if conn.sync_status in ("queued", "running") and not _is_stale(conn):
            continue
        try:
            sync_connection(db, conn)
            synced += 1
        except Exception:
            logger.exception("Scheduled sync failed for connection %s", conn.id)
            db.rollback()
    return synced
