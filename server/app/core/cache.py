"""A minimal in-process TTL cache.

Sufficient for a single-instance deployment at ~1000 users. For horizontal scale,
swap this for Redis behind the same interface.
"""
from __future__ import annotations

import threading
import time
from typing import Any

from app.core.config import settings


class TTLCache:
    def __init__(self, default_ttl: int | None = None) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl or settings.cache_ttl_seconds

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + (ttl or self._default_ttl), value)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            for k in [k for k in self._store if k.startswith(prefix)]:
                self._store.pop(k, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


cache = TTLCache()
