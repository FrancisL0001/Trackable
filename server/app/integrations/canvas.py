"""Canvas LMS provider.

Real mode uses the Canvas REST API with a user-supplied access token. Demo mode
returns realistic sample assignments.
"""
from __future__ import annotations

from datetime import datetime

import httpx

from app.core.config import settings
from app.core.errors import IntegrationError
from app.integrations import demo_data
from app.integrations.base import Integration, NormalizedItem
from app.models.enums import ItemKind, ItemPriority, ProviderType


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class CanvasIntegration(Integration):
    provider = ProviderType.CANVAS

    def validate(self) -> None:
        if self.demo:
            return
        if not self.secrets.get("token"):
            raise IntegrationError("Canvas connection requires an access token.")

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.canvas_items()
        self.validate()
        base_url = self.secrets.get("base_url") or settings.canvas_base_url
        token = self.secrets["token"]
        headers = {"Authorization": f"Bearer {token}"}
        items: list[NormalizedItem] = []
        try:
            with httpx.Client(base_url=base_url, headers=headers, timeout=15) as client:
                courses = client.get(
                    "/api/v1/courses", params={"enrollment_state": "active", "per_page": 50}
                )
                courses.raise_for_status()
                for course in courses.json():
                    cid = course.get("id")
                    cname = course.get("name", "")
                    resp = client.get(
                        f"/api/v1/courses/{cid}/assignments",
                        params={"per_page": 100, "order_by": "due_at"},
                    )
                    if resp.status_code != 200:
                        continue
                    for a in resp.json():
                        items.append(
                            NormalizedItem(
                                external_id=f"canvas-{a.get('id')}",
                                title=a.get("name", "Untitled assignment"),
                                kind=ItemKind.ASSIGNMENT,
                                course=cname,
                                description=(a.get("description") or "")[:2000],
                                url=a.get("html_url", ""),
                                due_at=_parse_dt(a.get("due_at")),
                                priority=ItemPriority.MEDIUM,
                            )
                        )
        except httpx.HTTPError as exc:
            raise IntegrationError(f"Canvas sync failed: {exc}") from exc
        return items
