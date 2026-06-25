"""Gradescope provider.

Gradescope has no official public API. Real integration requires authenticated
scraping with user-supplied credentials, which is brittle and best-effort. For the
MVP we ship demo data and clearly signal that live scraping is not enabled.
"""
from __future__ import annotations

from app.core.errors import IntegrationError
from app.integrations import demo_data
from app.integrations.base import Integration, NormalizedItem
from app.models.enums import ProviderType


class GradescopeIntegration(Integration):
    provider = ProviderType.GRADESCOPE

    def validate(self) -> None:
        if self.demo:
            return
        if not (self.secrets.get("email") and self.secrets.get("password")):
            raise IntegrationError(
                "Gradescope connection requires email and password."
            )

    def fetch_items(self) -> list[NormalizedItem]:
        if self.demo:
            return demo_data.gradescope_items()
        self.validate()
        # Live scraping is intentionally not implemented in the MVP. Surface a clear
        # error rather than silently returning nothing.
        raise IntegrationError(
            "Live Gradescope sync is not enabled in this build. Enable DEMO_MODE to "
            "preview Gradescope data, or import a Gradescope ICS feed via the ICS provider."
        )
