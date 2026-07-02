"""Safe-URL helpers.

Prevents unsafe URL schemes (e.g. ``javascript:``, ``data:``) from being stored on
items and later rendered into anchor hrefs by the client (a stored-XSS / phishing
vector). Only http(s) links are considered safe to render.
"""
from __future__ import annotations

from urllib.parse import urlparse

SAFE_SCHEMES = {"http", "https"}


def is_safe_web_url(url: str) -> bool:
    """True only for non-empty http/https URLs with a host."""
    if not url:
        return False
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False
    return parsed.scheme.lower() in SAFE_SCHEMES and bool(parsed.netloc)


def sanitize_web_url(url: str | None) -> str:
    """Return the URL if it is a safe web URL, otherwise an empty string.

    Used defensively for provider-synced items so untrusted upstream data cannot
    introduce dangerous links.
    """
    if url and is_safe_web_url(url):
        return url.strip()
    return ""
