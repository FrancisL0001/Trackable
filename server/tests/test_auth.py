"""Auth behavior: registration, login, token validation, and protection."""
from __future__ import annotations


def test_register_returns_token_and_user(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "new@uni.edu", "password": "password123", "full_name": "New"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "new@uni.edu"
    # Password material must never be returned.
    assert "password" not in body["user"]
    assert "hashed_password" not in body["user"]


def test_duplicate_email_rejected(client):
    payload = {"email": "dup@uni.edu", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_short_password_rejected(client):
    resp = client.post(
        "/api/auth/register", json={"email": "x@uni.edu", "password": "short"}
    )
    assert resp.status_code == 422


def test_login_success_and_wrong_password(client):
    client.post(
        "/api/auth/register", json={"email": "log@uni.edu", "password": "password123"}
    )
    ok = client.post(
        "/api/auth/login", json={"email": "log@uni.edu", "password": "password123"}
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post(
        "/api/auth/login", json={"email": "log@uni.edu", "password": "wrongpass1"}
    )
    assert bad.status_code == 401


def test_me_requires_valid_token(client, auth_headers):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401
    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["email"] == "student@uni.edu"
