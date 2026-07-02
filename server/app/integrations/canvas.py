"""Canvas LMS provider.

Real mode uses the Canvas REST API with a user-supplied access token, following
pagination links so large course/assignment lists sync completely. Demo mode
returns realistic sample assignments.
"""
from __future__ import annotations

from datetime import datetime

import httpx

from app.core.config import settings
from app.core.errors import IntegrationError
from app.core.ssrf import validate_public_url
from app.integrations import demo_data
from app.integrations.base import Integration, NormalizedItem
from app.models.enums import ItemKind, ItemPriority, ProviderType

# Budget per paginated endpoint so a pathological feed can't run away. Hitting
# the budget marks the sync as partial rather than silently truncating.
MAX_PAGES = 20


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class CanvasIntegration(Integration):
    provider = ProviderType.CANVAS

    # Overridable in tests to inject a mock transport.
    _transport: httpx.BaseTransport | None = None

    def validate(self) -> None:
        if self.demo:
            return
        if not self.secrets.get("token"):
            raise IntegrationError("Canvas connection requires an access token.")

    def _get_all_pages(self, client: httpx.Client, url: str, params: dict) -> list[dict]:
        """Follow Canvas Link-header pagination, up to MAX_PAGES pages."""
        results: list[dict] = []
        next_url: str | None = url
        next_params: dict | None = params
        for _ in range(MAX_PAGES):
            if next_url is None:
                return results
            resp = client.get(next_url, params=next_params)
            resp.raise_for_status()
            results.extend(resp.json())
            # rel="next" already encodes the query string; don't re-send params.
            next_url = resp.links.get("next", {}).get("url")
            next_params = None
        if next_url is not None:
            self.partial = True
            self.partial_reason = f"stopped after {MAX_PAGES} pages of {url}"
        return results

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.canvas_items()
        self.validate()
        base_url = self.secrets.get("base_url") or settings.canvas_base_url
        # Block SSRF and prevent leaking the bearer token to an internal/metadata
        # target. Validate the origin before attaching the token to any request.
        validate_public_url(base_url)
        token = self.secrets["token"]
        headers = {"Authorization": f"Bearer {token}"}
        items: list[NormalizedItem] = []
        try:
            # follow_redirects=False so a redirect can't forward the token elsewhere.
            with httpx.Client(
                base_url=base_url,
                headers=headers,
                timeout=15,
                follow_redirects=False,
                transport=self._transport,
            ) as client:
                courses = self._get_all_pages(
                    client,
                    "/api/v1/courses",
                    {"enrollment_state": "active", "per_page": 50},
                )
                for course in courses:
                    cid = course.get("id")
                    cname = course.get("name", "")
                    try:
                        assignments = self._get_all_pages(
                            client,
                            f"/api/v1/courses/{cid}/assignments",
                            {"per_page": 100, "order_by": "due_at"},
                        )
                    except httpx.HTTPStatusError:
                        # Some courses deny assignment access; note it and move on.
                        self.partial = True
                        self.partial_reason = f"could not read assignments for {cname or cid}"
                        continue
                    for a in assignments:
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
