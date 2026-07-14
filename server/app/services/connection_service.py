"""Manage integration connections and their encrypted secrets."""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import IntegrationError, NotFoundError, TrackableError
from app.core.security import decrypt_secret, encrypt_secret
from app.core.ssrf import validate_url_scheme
from app.integrations.registry import PROVIDER_CAPABILITIES, is_connectable
from app.models import Connection
from app.models.enums import ProviderType
from app.schemas.connection import ConnectionCreate

# URL-bearing secret keys per provider, validated (scheme/host) at connect time.
# Full SSRF validation (DNS + private-IP block) happens again at fetch time.
_URL_SECRET_KEYS: dict[ProviderType, tuple[str, ...]] = {
    ProviderType.ICS: ("url",),
    ProviderType.GOOGLE_CALENDAR: ("ical_url",),
    ProviderType.CANVAS: ("base_url",),
}


def _validate_secret_urls(provider: ProviderType, secrets: dict[str, str]) -> None:
    for key in _URL_SECRET_KEYS.get(provider, ()):
        value = secrets.get(key)
        if value:  # optional fields (e.g. Canvas base_url) are only checked if present
            try:
                validate_url_scheme(value)
            except IntegrationError as exc:
                # Bad user input at connect time → client error, not an upstream 502.
                raise TrackableError(f"Invalid {key}: {exc.message}") from exc


def _encrypt(secrets: dict[str, str]) -> str:
    if not secrets:
        return ""
    return encrypt_secret(json.dumps(secrets))


def decrypt_secrets(connection: Connection) -> dict[str, str]:
    if not connection.encrypted_secrets:
        return {}
    raw = decrypt_secret(connection.encrypted_secrets)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def list_connections(db: Session, owner_id: int) -> list[Connection]:
    return list(
        db.scalars(select(Connection).where(Connection.owner_id == owner_id)).all()
    )


def get(db: Session, owner_id: int, connection_id: int) -> Connection:
    conn = db.get(Connection, connection_id)
    if conn is None or conn.owner_id != owner_id:
        raise NotFoundError("Connection not found.")
    return conn


def upsert(db: Session, owner_id: int, data: ConnectionCreate) -> Connection:
    """Create a connection or update its secrets if the provider already exists."""
    if not is_connectable(data.provider):
        cap = PROVIDER_CAPABILITIES.get(data.provider)
        note = f" {cap.note}" if cap and cap.note else ""
        raise TrackableError(
            f"{data.provider.value} does not support live sync in this build.{note}"
        )
    if data.secrets:
        _validate_secret_urls(data.provider, data.secrets)
    existing = db.scalar(
        select(Connection).where(
            Connection.owner_id == owner_id, Connection.provider == data.provider
        )
    )
    if existing:
        existing.display_name = data.display_name or existing.display_name
        if data.secrets:
            existing.encrypted_secrets = _encrypt(data.secrets)
        existing.is_active = True
        # Fresh credentials deserve a fresh sync attempt.
        existing.sync_status = "idle"
        existing.next_sync_at = None
        db.commit()
        db.refresh(existing)
        return existing

    conn = Connection(
        owner_id=owner_id,
        provider=data.provider,
        display_name=data.display_name or data.provider.value.replace("_", " ").title(),
        encrypted_secrets=_encrypt(data.secrets),
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


def set_active(db: Session, owner_id: int, connection_id: int, active: bool) -> Connection:
    conn = get(db, owner_id, connection_id)
    conn.is_active = active
    db.commit()
    db.refresh(conn)
    return conn


def delete(db: Session, owner_id: int, connection_id: int) -> None:
    conn = get(db, owner_id, connection_id)
    db.delete(conn)
    db.commit()
