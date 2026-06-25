"""Manage integration connections and their encrypted secrets."""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.security import decrypt_secret, encrypt_secret
from app.models import Connection
from app.models.enums import ProviderType
from app.schemas.connection import ConnectionCreate


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
