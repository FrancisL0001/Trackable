"""Factory that builds the right Integration for a provider."""
from __future__ import annotations

from app.core.config import settings
from app.integrations.base import Integration
from app.integrations.canvas import CanvasIntegration
from app.integrations.google_calendar import GoogleCalendarIntegration
from app.integrations.gradescope import GradescopeIntegration
from app.integrations.ics import ICSIntegration
from app.models.enums import ProviderType

_REGISTRY: dict[ProviderType, type[Integration]] = {
    ProviderType.CANVAS: CanvasIntegration,
    ProviderType.GOOGLE_CALENDAR: GoogleCalendarIntegration,
    ProviderType.GRADESCOPE: GradescopeIntegration,
    ProviderType.ICS: ICSIntegration,
}

# Providers that users can connect (MANUAL is implicit, not an integration).
SUPPORTED_PROVIDERS = list(_REGISTRY.keys())


def build_integration(
    provider: ProviderType, secrets: dict[str, str], *, demo: bool | None = None
) -> Integration:
    if provider not in _REGISTRY:
        raise ValueError(f"Unsupported provider: {provider}")
    use_demo = settings.demo_mode if demo is None else demo
    return _REGISTRY[provider](secrets, demo=use_demo)
