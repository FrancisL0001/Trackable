"""Integration connections, demo-mode sync idempotency, and secret hiding."""
from __future__ import annotations


def _connect(client, headers, provider, secrets=None):
    body = {"provider": provider}
    if secrets:
        body["secrets"] = secrets
    return client.post("/api/integrations/connections", json=body, headers=headers)


def test_providers_endpoint_reports_demo_mode(client):
    body = client.get("/api/integrations/providers").json()
    assert "canvas" in body["providers"]
    assert isinstance(body["demo_mode"], bool)


def test_create_connection_never_returns_secrets(client, auth_headers):
    resp = _connect(client, auth_headers, "canvas", {"token": "supersecret"})
    assert resp.status_code == 201
    body = resp.json()
    assert "secret" not in str(body).lower() or "supersecret" not in str(body)
    assert "supersecret" not in str(body)


def test_sync_creates_items_then_is_idempotent(client, auth_headers):
    _connect(client, auth_headers, "canvas")
    first = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert first["total_created"] > 0

    second = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert second["total_created"] == 0  # no duplicates on re-sync


def test_disconnect_stops_contributions(client, auth_headers):
    conn = _connect(client, auth_headers, "canvas").json()
    client.post("/api/integrations/sync", headers=auth_headers)
    before = len(client.get("/api/items", headers=auth_headers).json())
    assert before > 0

    # Delete connection and its items are no longer refreshed; create a fresh user
    # to verify a deactivated connection does not sync.
    client.post(
        f"/api/integrations/connections/{conn['id']}/active?active=false",
        headers=auth_headers,
    )
    result = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert result["results"] == []


def test_sync_with_no_connections_is_empty(client, auth_headers):
    result = client.post("/api/integrations/sync", headers=auth_headers).json()
    assert result["results"] == []
    assert result["total_created"] == 0
