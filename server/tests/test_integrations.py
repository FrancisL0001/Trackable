"""Integration connections, background sync flow, idempotency, and secret hiding.

Note: with TestClient, FastAPI BackgroundTasks run before the response is
returned to the test, so "enqueue + background sync" completes synchronously
from the test's point of view.
"""
from __future__ import annotations


def _connect(client, headers, provider, secrets=None):
    body = {"provider": provider}
    if secrets:
        body["secrets"] = secrets
    return client.post("/api/integrations/connections", json=body, headers=headers)


def _items_total(client, headers) -> int:
    return client.get("/api/items", headers=headers).json()["total"]


def _connections(client, headers):
    return client.get("/api/integrations/connections", headers=headers).json()


def test_providers_endpoint_reports_capabilities(client):
    body = client.get("/api/integrations/providers").json()
    assert isinstance(body["demo_mode"], bool)
    assert body["sync_interval_minutes"] > 0
    ids = [p["id"] for p in body["providers"]]
    assert "canvas" in ids
    gradescope = next(p for p in body["providers"] if p["id"] == "gradescope")
    assert gradescope["live_supported"] is False
    gcal = next(p for p in body["providers"] if p["id"] == "google_calendar")
    assert "iCal" in gcal["label"]  # honest naming: feed import, not OAuth


def test_create_connection_never_returns_secrets(client, auth_headers):
    resp = _connect(client, auth_headers, "canvas", {"token": "supersecret"})
    assert resp.status_code == 201
    assert "supersecret" not in str(resp.json())


def test_connect_triggers_initial_sync(client, auth_headers):
    _connect(client, auth_headers, "canvas")
    # Background sync ran during the request; items exist without a manual sync.
    assert _items_total(client, auth_headers) > 0
    conn = _connections(client, auth_headers)[0]
    assert conn["sync_status"] == "ok"
    assert conn["last_synced_at"] is not None
    assert conn["next_sync_at"] is not None  # scheduler will keep it fresh


def test_sync_is_idempotent(client, auth_headers):
    _connect(client, auth_headers, "canvas")
    total_after_connect = _items_total(client, auth_headers)
    assert total_after_connect > 0

    resp = client.post("/api/integrations/sync", headers=auth_headers)
    assert resp.status_code == 202
    assert _items_total(client, auth_headers) == total_after_connect  # no duplicates


def test_deactivated_connection_is_not_queued(client, auth_headers):
    conn = _connect(client, auth_headers, "canvas").json()
    client.post(
        f"/api/integrations/connections/{conn['id']}/active?active=false",
        headers=auth_headers,
    )
    result = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert result["queued"] == []


def test_sync_with_no_connections_queues_nothing(client, auth_headers):
    result = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert result["queued"] == []


def test_connect_rejects_non_https_feed_url(client, auth_headers):
    resp = _connect(client, auth_headers, "ics", {"url": "http://localhost/feed.ics"})
    assert resp.status_code == 400


def test_connect_rejects_unsafe_ical_url(client, auth_headers):
    resp = _connect(
        client, auth_headers, "google_calendar", {"ical_url": "javascript:alert(1)"}
    )
    assert resp.status_code == 400


def test_connect_accepts_https_feed_url(client, auth_headers):
    resp = _connect(client, auth_headers, "ics", {"url": "https://example.com/feed.ics"})
    assert resp.status_code == 201


def test_gradescope_not_connectable_in_live_mode(client, auth_headers, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "demo_mode", False)
    resp = _connect(
        client, auth_headers, "gradescope", {"email": "a@b.edu", "password": "x"}
    )
    assert resp.status_code == 400
    assert "live sync" in resp.json()["detail"].lower()

    providers = client.get("/api/integrations/providers").json()["providers"]
    assert "gradescope" not in [p["id"] for p in providers]


def test_user_edits_survive_resync(client, auth_headers):
    _connect(client, auth_headers, "canvas")
    items = client.get("/api/items?source=canvas", headers=auth_headers).json()["items"]
    item = items[0]

    patched = client.patch(
        f"/api/items/{item['id']}",
        json={"title": "My renamed assignment", "priority": "high"},
        headers=auth_headers,
    ).json()
    assert patched["user_edited_fields"] == ["title"]  # priority isn't provider-owned

    client.post("/api/integrations/sync", headers=auth_headers)
    after = client.get(f"/api/items/{item['id']}", headers=auth_headers).json()
    assert after["title"] == "My renamed assignment"  # edit preserved
    assert after["priority"] == "high"
