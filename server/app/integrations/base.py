"""Integration adapter contract.

Every provider implements ``fetch_items`` and returns ``NormalizedItem``s. The sync
service upserts these into the unified ``Item`` table. Each provider supports a demo
mode so the whole app is runnable without real credentials.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime

from app.models.enums import ItemKind, ItemPriority, ProviderType


@dataclass
class NormalizedItem:
    """Provider-agnostic representation of a synced item."""

    external_id: str
    title: str
    kind: ItemKind = ItemKind.ASSIGNMENT
    description: str = ""
    course: str = ""
    location: str = ""
    url: str = ""
    start_at: datetime | None = None
    due_at: datetime | None = None
    priority: ItemPriority = ItemPriority.MEDIUM
    extra: dict = field(default_factory=dict)


class Integration(abc.ABC):
    """Base class for all provider adapters."""

    provider: ProviderType

    def __init__(self, secrets: dict[str, str], *, demo: bool = False) -> None:
        self.secrets = secrets or {}
        self.demo = demo
        # Set by fetch_items when the provider response could not be fully
        # consumed (e.g. pagination budget hit). Partial data is surfaced to the
        # user instead of being silently reported as a full sync.
        self.partial = False
        self.partial_reason = ""

    @abc.abstractmethod
    def fetch_items(self) -> list[NormalizedItem]:
        """Return the current set of items from the provider."""

    def validate(self) -> None:
        """Raise IntegrationError if required secrets are missing (non-demo)."""
        return None
