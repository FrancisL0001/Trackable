"""Factory that builds the right Integration for a provider, plus capability
metadata so the API/client can present each provider honestly (e.g. Gradescope
is demo-only, Google Calendar is an iCal feed import rather than OAuth)."""
from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class ProviderCapability:
    """What a provider can actually do, surfaced through /providers."""

    provider: ProviderType
    label: str
    description: str
    # False -> only demo mode works; connecting live is rejected server-side.
    live_supported: bool
    # Short honest note about how the live integration works / its limits.
    note: str = ""


PROVIDER_CAPABILITIES: dict[ProviderType, ProviderCapability] = {
    ProviderType.CANVAS: ProviderCapability(
        provider=ProviderType.CANVAS,
        label="Canvas",
        description="Sync assignments and due dates from your Canvas courses.",
        live_supported=True,
        note="Uses a personal access token (Canvas → Account → Settings).",
    ),
    ProviderType.GOOGLE_CALENDAR: ProviderCapability(
        provider=ProviderType.GOOGLE_CALENDAR,
        label="Google Calendar (iCal feed)",
        description="Pull in events and meetings via your calendar's secret iCal URL.",
        live_supported=True,
        note=(
            "Imports the secret iCal feed (Calendar settings → 'Secret address in "
            "iCal format'). Full Google account OAuth is not part of this build."
        ),
    ),
    ProviderType.GRADESCOPE: ProviderCapability(
        provider=ProviderType.GRADESCOPE,
        label="Gradescope",
        description="Preview Gradescope homework and submission deadlines.",
        live_supported=False,
        note=(
            "Gradescope has no public API, so live sync is demo-only for now. "
            "Import a Gradescope ICS feed via the ICS provider instead."
        ),
    ),
    ProviderType.ICS: ProviderCapability(
        provider=ProviderType.ICS,
        label="Calendar feed (ICS)",
        description="Import any calendar feed from a course website or portal.",
        live_supported=True,
        note="Works with any public or secret .ics URL.",
    ),
}


def connectable_providers() -> list[ProviderCapability]:
    """Providers a user may connect given the server mode (demo vs live)."""
    caps = [PROVIDER_CAPABILITIES[p] for p in SUPPORTED_PROVIDERS]
    if settings.demo_mode:
        return caps
    return [c for c in caps if c.live_supported]


def is_connectable(provider: ProviderType) -> bool:
    cap = PROVIDER_CAPABILITIES.get(provider)
    if cap is None:
        return False
    return settings.demo_mode or cap.live_supported


def build_integration(
    provider: ProviderType, secrets: dict[str, str], *, demo: bool | None = None
) -> Integration:
    if provider not in _REGISTRY:
        raise ValueError(f"Unsupported provider: {provider}")
    use_demo = settings.demo_mode if demo is None else demo
    return _REGISTRY[provider](secrets, demo=use_demo)
