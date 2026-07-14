"""Minimal in-process periodic sync scheduler.

A single daemon thread wakes up every ``tick_seconds`` and refreshes any active
connection whose ``next_sync_at`` has passed. This matches the documented
single-instance MVP deployment (see docs/DEPLOYMENT.md); the startup guard in
``app.core.startup`` refuses multi-worker production configs so two schedulers
can't race. If the app outgrows one instance, replace this with a real worker
queue behind the same ``sync_due_connections`` entry point.
"""
from __future__ import annotations

import logging
import threading

from app.core import database
from app.core.config import settings

logger = logging.getLogger("trackable.scheduler")


class SyncScheduler:
    def __init__(self, tick_seconds: int | None = None) -> None:
        self._tick = tick_seconds or settings.sync_scheduler_tick_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _run_once(self) -> None:
        from app.services import sync_service

        db = database.SessionLocal()
        try:
            synced = sync_service.sync_due_connections(db)
            if synced:
                logger.info("Scheduled sync refreshed %d connection(s)", synced)
        except Exception:
            logger.exception("Scheduled sync tick failed")
        finally:
            db.close()

    def _loop(self) -> None:
        while not self._stop.wait(self._tick):
            self._run_once()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._loop, name="trackable-sync-scheduler", daemon=True
        )
        self._thread.start()
        logger.info(
            "Sync scheduler started (every %ss; connections refresh every %s min)",
            self._tick,
            settings.sync_interval_minutes,
        )

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None


scheduler = SyncScheduler()
