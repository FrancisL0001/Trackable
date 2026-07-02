"""URL safety helpers and item URL validation."""
from __future__ import annotations

import pytest

from app.core.urls import is_safe_web_url, sanitize_web_url


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/x", True),
        ("http://example.com", True),
        ("javascript:alert(1)", False),
        ("data:text/html,<script>", False),
        ("//evil.com", False),
        ("ftp://example.com", False),
        ("", False),
        ("not a url", False),
    ],
)
def test_is_safe_web_url(url, expected):
    assert is_safe_web_url(url) is expected


def test_sanitize_drops_unsafe_and_keeps_safe():
    assert sanitize_web_url("javascript:alert(1)") == ""
    assert sanitize_web_url(None) == ""
    assert sanitize_web_url("https://example.com") == "https://example.com"


def test_item_create_rejects_unsafe_url(client, auth_headers):
    resp = client.post(
        "/api/items",
        json={"title": "Bad link", "url": "javascript:alert(1)"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_item_create_accepts_safe_url(client, auth_headers):
    resp = client.post(
        "/api/items",
        json={"title": "Good link", "url": "https://canvas.example.edu/a/1"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["url"] == "https://canvas.example.edu/a/1"
