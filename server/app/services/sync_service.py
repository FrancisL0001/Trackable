"""Pull items from connected providers and upsert them idempotently."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.core.errors import IntegrationError
from app.core.timeutils import utcnow
from app.integrations.base import NormalizedItem
from app.integrations.registry import build_integration
from app.models import Connection, Item
from app.models.enums import ItemStatus, ProviderType
from app.services import connection_service


def _upsert_item(
    db: Session, owner_id: int, source: ProviderType, n: NormalizedItem
) -> bool:
    """Insert or update one normalized item. Returns True if newly created."""
    existing = db.scalar(
        select(Item).where(
            Item.owner_id == owner_id,
            Item.source == source,
            Item.external_id == n.external_id,
        )
    )
    if existing:
        # Preserve user-set status/completion; refresh provider-owned fields.
        existing.title = n.title
        existing.description = n.description
        existing.kind = n.kind
        existing.course = n.course
        existing.location = n.location
        existing.url = n.url
        existing.start_at = n.start_at
        existing.due_at = n.due_at
        return False

    db.add(
        Item(
            owner_id=owner_id,
            source=source,
            external_id=n.external_id,
            title=n.title,
            description=n.description,
            kind=n.kind,
            status=ItemStatus.TODO,
            priority=n.priority,
            course=n.course,
            location=n.location,
            url=n.url,
            start_at=n.start_at,
            due_at=n.due_at,
        )
    )
    return True


def sync_connection(db: Session, owner_id: int, connection: Connection) -> dict:
    secrets = connection_service.decrypt_secrets(connection)
    integration = build_integration(connection.provider, secrets)
    created = updated = 0
    try:
        items = integration.fetch_items()
        for n in items:
            if _upsert_item(db, owner_id, connection.provider, n):
                created += 1
            else:
                updated += 1
        connection.last_sync_status = f"ok: {len(items)} items"
        status = "ok"
        total = len(items)
    except IntegrationError as exc:
        connection.last_sync_status = f"error: {exc.message}"
        status = "error"
        total = 0
    connection.last_synced_at = utcnow()
    db.commit()
    cache.invalidate_prefix(f"dashboard:{owner_id}")
    return {
        "provider": connection.provider,
        "created": created,
        "updated": updated,
        "total": total,
        "status": status,
    }


def sync_all(db: Session, owner_id: int) -> dict:
    connections = [
        c for c in connection_service.list_connections(db, owner_id) if c.is_active
    ]
    results = [sync_connection(db, owner_id, c) for c in connections]
    return {
        "results": results,
        "total_created": sum(r["created"] for r in results),
        "total_updated": sum(r["updated"] for r in results),
    }
