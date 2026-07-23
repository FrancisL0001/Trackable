"""Course-website (web_page) provider: HTML stripping, LLM extraction mapping,
stable IDs, hash-based skip, and live-mode config gating."""
from __future__ import annotations

import pytest

from app.core.config import settings
from app.integrations import llm
from app.integrations.web_page import WebPageIntegration, _stable_id, html_to_text
from app.models import Connection
from app.models.enums import ItemKind, ProviderType
from app.schemas.auth import UserCreate
from app.services import sync_service, user_service

PAGE_V1 = b"""
<html><head><style>.x{color:red}</style><script>alert(1)</script></head>
<body><h1>CS 0220 Assignments</h1>
<table><tr><td><a href="/hw1.pdf">Homework 1</a></td><td>due Sep 12</td></tr></table>
</body></html>
"""
PAGE_V2 = PAGE_V1.replace(b"Homework 1", b"Homework 1 (updated)")

EXTRACTED = [
    {
        "title": "Homework 1",
        "due_at": "2026-09-12T23:59:00",
        "kind": "assignment",
        "url": "https://cs.example.edu/hw1.pdf",
        "description": "First homework",
    },
    {"title": "Midterm", "due_at": "2026-10-20T14:00:00Z", "kind": "exam", "url": None},
    {"title": "", "kind": "assignment"},  # no title -> dropped by llm parser upstream
]


def test_html_to_text_strips_scripts_and_keeps_links():
    text = html_to_text(PAGE_V1)
    assert "alert" not in text and "color:red" not in text
    assert "Homework 1" in text and "due Sep 12" in text
    assert "[link: /hw1.pdf]" in text


def test_stable_id_ignores_case_and_whitespace():
    assert _stable_id("Homework 1") == _stable_id("  homework   1 ")
    assert _stable_id("Homework 1") != _stable_id("Homework 2")


def test_parse_items_tolerates_prose_fences_and_both_shapes():
    prose = 'Sure! Here are the deadlines:\n[{"title": "HW 1"}]\nLet me know!'
    assert llm._parse_items(prose) == [{"title": "HW 1"}]
    fenced = '```json\n{"items": [{"title": "HW 2"}]}\n```'
    assert llm._parse_items(fenced) == [{"title": "HW 2"}]
    assert llm._parse_items('{"items": []}') == []
    with pytest.raises(ValueError):
        llm._parse_items("no json here")


@pytest.fixture
def fake_llm(monkeypatch):
    """Point the extractor at a fake backend and record calls."""
    calls: list[str] = []

    def fake_extract(text, source_url, now=None):
        calls.append(text)
        return [dict(r) for r in EXTRACTED]

    monkeypatch.setattr(settings, "llm_base_url", "http://fake-ollama:11434/v1")
    monkeypatch.setattr("app.integrations.web_page.llm.extract_deadlines", fake_extract)
    return calls


def _integration(monkeypatch, page: bytes) -> WebPageIntegration:
    monkeypatch.setattr("app.integrations.web_page.safe_get", lambda url: page)
    return WebPageIntegration({"url": "https://cs.example.edu/assignments"}, demo=False)


def test_extraction_maps_to_normalized_items(monkeypatch, fake_llm):
    integ = _integration(monkeypatch, PAGE_V1)
    items = integ.fetch_items()

    assert [i.title for i in items] == ["Homework 1", "Midterm"]
    hw, midterm = items
    assert hw.kind == ItemKind.ASSIGNMENT
    assert hw.url == "https://cs.example.edu/hw1.pdf"
    assert hw.due_at is not None and hw.due_at.tzinfo is not None
    assert midterm.kind == ItemKind.EXAM
    # No item URL -> falls back to the page, so users can verify the extraction.
    assert midterm.url == "https://cs.example.edu/assignments"
    # Same titles always map to the same ids (updates, not duplicates).
    assert items[0].external_id == _stable_id("Homework 1")
    assert integ.content_hash and not integ.unchanged


def test_unchanged_page_skips_the_model(monkeypatch, fake_llm):
    first = _integration(monkeypatch, PAGE_V1)
    first.fetch_items()

    second = _integration(monkeypatch, PAGE_V1)
    second.previous_hash = first.content_hash
    assert second.fetch_items() == []
    assert second.unchanged is True
    assert len(fake_llm) == 1  # model called once, not twice

    changed = _integration(monkeypatch, PAGE_V2)
    changed.previous_hash = first.content_hash
    assert changed.fetch_items() != []
    assert changed.unchanged is False
    assert len(fake_llm) == 2


def test_sync_persists_hash_and_reports_unchanged(db_session, monkeypatch, fake_llm):
    monkeypatch.setattr("app.integrations.web_page.safe_get", lambda url: PAGE_V1)
    monkeypatch.setattr(settings, "demo_mode", False)
    user = user_service.register(
        db_session, UserCreate(email="wp@uni.edu", password="password123")
    )
    conn = Connection(owner_id=user.id, provider=ProviderType.WEB_PAGE, display_name="CS 0220")
    db_session.add(conn)
    db_session.commit()
    # No secrets stored -> inject the URL at decrypt time for this test.
    monkeypatch.setattr(
        "app.services.sync_service.connection_service.decrypt_secrets",
        lambda c: {"url": "https://cs.example.edu/assignments"},
    )

    first = sync_service.sync_connection(db_session, conn)
    assert first["created"] == 2 and first["status"] == "ok"
    assert conn.last_content_hash != ""

    second = sync_service.sync_connection(db_session, conn)
    assert second == {
        "provider": ProviderType.WEB_PAGE,
        "created": 0,
        "updated": 0,
        "total": 0,
        "status": "ok",
    }
    assert "unchanged" in conn.last_sync_status
    assert len(fake_llm) == 1  # extraction ran only on the first sync


def test_web_page_gated_when_no_model_configured(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", False)
    monkeypatch.setattr(settings, "llm_base_url", "")
    monkeypatch.setattr(settings, "anthropic_api_key", "")

    providers = client.get("/api/integrations/providers").json()["providers"]
    assert "web_page" not in [p["id"] for p in providers]

    resp = client.post(
        "/api/integrations/connections",
        json={"provider": "web_page", "secrets": {"url": "https://cs.example.edu/a"}},
        headers=auth_headers,
    )
    assert resp.status_code == 400

    # With a model configured (e.g. local Ollama), it becomes connectable.
    monkeypatch.setattr(settings, "llm_base_url", "http://localhost:11434/v1")
    providers = client.get("/api/integrations/providers").json()["providers"]
    assert "web_page" in [p["id"] for p in providers]
