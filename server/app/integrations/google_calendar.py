"""Google Calendar provider.

Full OAuth2 is out of scope for the MVP. In real mode we support the pragmatic and
common path of a *secret iCal URL* (Calendar settings → "Secret address in iCal
format"), parsed via the ICS logic. Demo mode returns sample meetings/events.
"""
from __future__ import annotations

from app.core.errors import IntegrationError
from app.integrations import demo_data
from app.integrations.base import Integration, NormalizedItem
from app.integrations.ics import ICSIntegration
from app.models.enums import ItemKind, ProviderType


class GoogleCalendarIntegration(Integration):
    provider = ProviderType.GOOGLE_CALENDAR

    def validate(self) -> None:
        if self.demo:
            return
        if not self.secrets.get("ical_url"):
            raise IntegrationError(
                "Google Calendar connection requires a secret iCal URL "
                "(Calendar settings → Secret address in iCal format)."
            )

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.google_calendar_items()
        self.validate()
        # Reuse ICS parsing for the secret iCal feed, then mark items as meetings/events.
        ics = ICSIntegration({"url": self.secrets["ical_url"]}, demo=False)
        items = ics.fetch_items()
        for item in items:
            item.kind = ItemKind.MEETING if item.start_at else ItemKind.EVENT
            item.external_id = item.external_id.replace("ics-", "gcal-", 1)
        return items
