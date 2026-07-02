"""Generic ICS / iCalendar feed provider.

Used for course websites and any calendar that exposes a public/secret ICS URL.
Real mode downloads and parses the feed; demo mode returns sample deadlines.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone

import httpx
from icalendar import Calendar

from app.core.errors import IntegrationError
from app.core.ssrf import safe_get
from app.integrations import demo_data
from app.integrations.base import Integration, NormalizedItem
from app.models.enums import ItemKind, ProviderType


def _to_datetime(value) -> datetime | None:
    if value is None:
        return None
    dt = getattr(value, "dt", value)
    if isinstance(dt, datetime):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    if isinstance(dt, date):
        return datetime.combine(dt, time(23, 59), tzinfo=timezone.utc)
    return None


class ICSIntegration(Integration):
    provider = ProviderType.ICS

    def validate(self) -> None:
        if self.demo:
            return
        if not self.secrets.get("url"):
            raise IntegrationError("ICS connection requires a calendar feed URL.")

    def _parse(self, raw: bytes) -> list[NormalizedItem]:
        cal = Calendar.from_ical(raw)
        items: list[NormalizedItem] = []
        for component in cal.walk("VEVENT"):
            uid = str(component.get("uid", ""))
            summary = str(component.get("summary", "Untitled event"))
            start = _to_datetime(component.get("dtstart"))
            end = _to_datetime(component.get("dtend")) or start
            items.append(
                NormalizedItem(
                    external_id=f"ics-{uid}" if uid else f"ics-{summary}-{start}",
                    title=summary,
                    kind=ItemKind.DEADLINE,
                    description=str(component.get("description", ""))[:2000],
                    location=str(component.get("location", "")),
                    start_at=start,
                    due_at=end,
                )
            )
        return items

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.ics_items()
        self.validate()
        url = self.secrets["url"]
        try:
            raw = safe_get(url)
            return self._parse(raw)
        except httpx.HTTPError as exc:
            raise IntegrationError(f"ICS sync failed: {exc}") from exc
        except ValueError as exc:
            raise IntegrationError(f"Could not parse ICS feed: {exc}") from exc
