"""Item CRUD, ownership isolation, completion, and filtering."""
from __future__ import annotations


def _make_item(client, headers, **overrides):
    payload = {"title": "Read chapter 3", "kind": "task", "course": "CS 200"}
    payload.update(overrides)
    return client.post("/api/items", json=payload, headers=headers)


def test_create_and_get_item(client, auth_headers):
    resp = _make_item(client, auth_headers, due_at="2030-01-01T12:00:00Z")
    assert resp.status_code == 201
    item = resp.json()
    assert item["title"] == "Read chapter 3"
    assert item["source"] == "manual"
    assert item["status"] == "todo"

    got = client.get(f"/api/items/{item['id']}", headers=auth_headers)
    assert got.status_code == 200
    assert got.json()["id"] == item["id"]


def test_blank_title_rejected(client, auth_headers):
    resp = _make_item(client, auth_headers, title="   ")
    assert resp.status_code == 422


def test_complete_toggle_sets_completed_at(client, auth_headers):
    item = _make_item(client, auth_headers).json()
    done = client.post(f"/api/items/{item['id']}/complete", headers=auth_headers)
    assert done.status_code == 200
    assert done.json()["status"] == "done"
    assert done.json()["completed_at"] is not None

    reopened = client.post(
        f"/api/items/{item['id']}/complete?completed=false", headers=auth_headers
    )
    assert reopened.json()["status"] == "todo"
    assert reopened.json()["completed_at"] is None


def test_update_item(client, auth_headers):
    item = _make_item(client, auth_headers).json()
    resp = client.patch(
        f"/api/items/{item['id']}",
        json={"title": "Updated", "priority": "high"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"
    assert resp.json()["priority"] == "high"


def test_delete_item(client, auth_headers):
    item = _make_item(client, auth_headers).json()
    assert client.delete(f"/api/items/{item['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/items/{item['id']}", headers=auth_headers).status_code == 404


def test_filtering_by_kind_and_search(client, auth_headers):
    _make_item(client, auth_headers, title="Essay draft", kind="assignment")
    _make_item(client, auth_headers, title="Gym session", kind="event")

    only_assignments = client.get(
        "/api/items?kind=assignment", headers=auth_headers
    ).json()["items"]
    assert all(i["kind"] == "assignment" for i in only_assignments)

    search = client.get("/api/items?search=gym", headers=auth_headers).json()["items"]
    assert len(search) == 1
    assert search[0]["title"] == "Gym session"


def test_items_are_isolated_per_user(client, auth_headers):
    mine = _make_item(client, auth_headers).json()

    other = client.post(
        "/api/auth/register",
        json={"email": "other@uni.edu", "password": "password123"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    # The other user cannot see or fetch my item.
    assert client.get("/api/items", headers=other_headers).json()["items"] == []
    assert client.get(f"/api/items/{mine['id']}", headers=other_headers).status_code == 404


def test_list_pagination_metadata(client, auth_headers):
    for i in range(5):
        _make_item(client, auth_headers, title=f"Task {i}")

    page = client.get("/api/items?limit=2&offset=0", headers=auth_headers).json()
    assert page["total"] == 5
    assert page["limit"] == 2
    assert page["has_more"] is True
    assert len(page["items"]) == 2

    last = client.get("/api/items?limit=2&offset=4", headers=auth_headers).json()
    assert len(last["items"]) == 1
    assert last["has_more"] is False


def test_list_filter_by_multiple_kinds(client, auth_headers):
    _make_item(client, auth_headers, title="PSet", kind="assignment")
    _make_item(client, auth_headers, title="Midterm", kind="exam")
    _make_item(client, auth_headers, title="Gym", kind="event")

    page = client.get("/api/items?kinds=assignment,exam", headers=auth_headers).json()
    assert page["total"] == 2
    assert {i["kind"] for i in page["items"]} == {"assignment", "exam"}

    bad = client.get("/api/items?kinds=assignment,nope", headers=auth_headers)
    assert bad.status_code == 422
