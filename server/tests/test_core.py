"""Tests for cross-cutting core utilities: cache, security, time."""
from __future__ import annotations

import time
from datetime import datetime, timezone

from app.core.cache import TTLCache
from app.core.security import (
    create_access_token,
    decode_access_token,
    decrypt_secret,
    encrypt_secret,
    hash_password,
    verify_password,
)
from app.core.timeutils import ensure_aware


def test_password_hash_roundtrip():
    hashed = hash_password("password123")
    assert hashed != "password123"
    assert verify_password("password123", hashed)
    assert not verify_password("wrongpass", hashed)


def test_jwt_roundtrip_and_invalid():
    token = create_access_token(123)
    assert decode_access_token(token) == "123"
    assert decode_access_token("not-a-token") is None


def test_secret_encryption_roundtrip():
    enc = encrypt_secret("my-canvas-token")
    assert enc != "my-canvas-token"
    assert decrypt_secret(enc) == "my-canvas-token"
    assert decrypt_secret("garbage") is None


def test_cache_ttl_expires():
    cache = TTLCache(default_ttl=100)
    cache.set("k", "v", ttl=1)
    assert cache.get("k") == "v"
    time.sleep(1.1)
    assert cache.get("k") is None


def test_cache_invalidate_prefix():
    cache = TTLCache()
    cache.set("dashboard:1", "a")
    cache.set("dashboard:2", "b")
    cache.set("other", "c")
    cache.invalidate_prefix("dashboard:")
    assert cache.get("dashboard:1") is None
    assert cache.get("other") == "c"


def test_ensure_aware_treats_naive_as_utc():
    naive = datetime(2030, 1, 1, 12, 0, 0)
    aware = ensure_aware(naive)
    assert aware.tzinfo is not None
    assert aware == datetime(2030, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
