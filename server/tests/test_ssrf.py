"""SSRF protections for user-supplied integration URLs."""
from __future__ import annotations

import pytest

from app.core.errors import IntegrationError
from app.core.ssrf import safe_get, validate_public_url, validate_url_scheme


def test_scheme_validation_requires_https():
    assert validate_url_scheme("https://example.com/feed.ics") == "https://example.com/feed.ics"
    for bad in ["http://example.com", "javascript:alert(1)", "file:///etc/passwd", ""]:
        with pytest.raises(IntegrationError):
            validate_url_scheme(bad)


def test_scheme_validation_requires_host():
    with pytest.raises(IntegrationError):
        validate_url_scheme("https:///nohost")


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1/x",
        "https://10.0.0.5/x",
        "https://192.168.1.1/x",
        "https://169.254.169.254/latest/meta-data/",  # cloud metadata
        "https://[::1]/x",
        "http://8.8.8.8/x",  # public IP but wrong scheme
    ],
)
def test_validate_public_url_blocks_unsafe_targets(url):
    with pytest.raises(IntegrationError):
        validate_public_url(url)


def test_validate_public_url_allows_public_ip_literal():
    # IP literal avoids DNS; 1.1.1.1 is globally routable.
    assert validate_public_url("https://1.1.1.1/feed.ics") == "https://1.1.1.1/feed.ics"


def test_safe_get_blocks_internal_target_without_network():
    # Validation fails before any socket connection is attempted.
    with pytest.raises(IntegrationError):
        safe_get("https://127.0.0.1/secret")
