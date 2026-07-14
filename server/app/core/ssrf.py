"""SSRF-resistant outbound HTTP for user-supplied integration URLs.

User-controlled URLs (ICS feeds, Google secret iCal links, Canvas base URL) are fetched
by the server, so they must be constrained to prevent the backend from being tricked into
hitting internal/metadata services. This module enforces:

- https only (no http/file/gopher/etc.),
- DNS resolution + rejection of non-public IPs (loopback, private, link-local,
  multicast, reserved, and the cloud metadata range 169.254.169.254),
- redirects followed manually with re-validation at every hop (no blind redirects),
- a response size cap.

Residual risk: DNS rebinding between validation and connection is not fully mitigated
(would require pinning the resolved IP at the socket layer). Acceptable for this scale;
documented for future hardening.
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from app.core.errors import IntegrationError

ALLOWED_SCHEMES = {"https"}
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_REDIRECTS = 3
DEFAULT_TIMEOUT = 15.0


def validate_url_scheme(url: str) -> str:
    """Cheap, no-DNS check used at connection-create time for fast feedback."""
    if not url or not url.strip():
        raise IntegrationError("A URL is required.")
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise IntegrationError("Only https:// URLs are allowed.")
    if not parsed.hostname:
        raise IntegrationError("URL is missing a host.")
    return url.strip()


def _resolve_ips(host: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise IntegrationError(f"Could not resolve host '{host}'.") from exc
    return list({info[4][0] for info in infos})


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    # is_global excludes private/loopback/link-local/reserved/unspecified.
    return ip.is_global and not ip.is_multicast


def validate_public_url(url: str) -> str:
    """Full validation: https scheme + every resolved IP must be public."""
    cleaned = validate_url_scheme(url)
    host = urlparse(cleaned).hostname
    assert host is not None  # guaranteed by validate_url_scheme
    ips = _resolve_ips(host)
    if not ips:
        raise IntegrationError(f"Host '{host}' did not resolve to any address.")
    for ip in ips:
        if not _is_public_ip(ip):
            raise IntegrationError(
                f"URL host resolves to a non-public address ({ip}); blocked."
            )
    return cleaned


def safe_get(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_bytes: int = MAX_RESPONSE_BYTES,
    max_redirects: int = MAX_REDIRECTS,
) -> bytes:
    """GET a user-supplied URL safely, validating the target at every redirect hop."""
    current = url
    with httpx.Client(follow_redirects=False, timeout=timeout) as client:
        for _ in range(max_redirects + 1):
            validate_public_url(current)
            resp = client.get(current, headers=headers)
            if resp.is_redirect:
                location = resp.headers.get("location")
                if not location:
                    raise IntegrationError("Redirect response missing a location.")
                current = str(httpx.URL(current).join(location))
                continue
            resp.raise_for_status()
            declared = resp.headers.get("content-length")
            if declared and declared.isdigit() and int(declared) > max_bytes:
                raise IntegrationError("Remote response is too large.")
            content = resp.content
            if len(content) > max_bytes:
                raise IntegrationError("Remote response is too large.")
            return content
    raise IntegrationError("Too many redirects while fetching the URL.")
