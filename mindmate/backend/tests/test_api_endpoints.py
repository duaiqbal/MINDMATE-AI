"""Tests for mood/memory/consent endpoints using fake auth + in-memory repo."""

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user_id, get_repository
from app.db.repository import InMemoryRepository
from app.main import create_app


@pytest.fixture
def client_for():
    """client_for(user_id) -> TestClient. All clients share ONE repo, but each
    gets its own app bound to a fixed user, so creating a second client does
    not rebind the first client's identity."""
    repo = InMemoryRepository()

    def _make(user_id: str) -> TestClient:
        app = create_app()
        app.dependency_overrides[get_repository] = lambda: repo
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return TestClient(app)

    return _make


def test_create_and_trend_mood(client_for):
    c = client_for("user-1")
    r = c.post("/v1/mood", json={"mood": 4, "note": "ok day"})
    assert r.status_code == 201
    assert r.json()["mood"] == 4

    t = c.get("/v1/mood/trends?window_days=7")
    assert t.status_code == 200
    body = t.json()
    assert body["window_days"] == 7
    assert body["points"][0]["count"] == 1
    assert body["points"][0]["average_mood"] == 4.0


def test_mood_validation_rejects_out_of_range(client_for):
    c = client_for("user-1")
    assert c.post("/v1/mood", json={"mood": 9}).status_code == 422
    assert c.post("/v1/mood", json={"mood": 0}).status_code == 422


def test_memory_crud(client_for):
    c = client_for("user-1")
    created = c.post("/v1/memory", json={"content": "remember this"})
    assert created.status_code == 201
    item_id = created.json()["id"]

    listed = c.get("/v1/memory").json()
    assert len(listed["items"]) == 1

    patched = c.patch(f"/v1/memory/{item_id}", json={"content": "updated"})
    assert patched.status_code == 200
    assert patched.json()["content"] == "updated"

    deleted = c.delete(f"/v1/memory/{item_id}")
    assert deleted.status_code == 204
    assert c.get("/v1/memory").json()["items"] == []


def test_memory_update_missing_is_404(client_for):
    c = client_for("user-1")
    assert c.patch("/v1/memory/nope", json={"content": "x"}).status_code == 404
    assert c.delete("/v1/memory/nope").status_code == 404


def test_consent_grant_and_list(client_for):
    c = client_for("user-1")
    r = c.post("/v1/consent", json={"consent_type": "data_processing"})
    assert r.status_code == 201
    assert r.json()["consent_type"] == "data_processing"
    assert r.json()["revoked_at"] is None
    assert len(c.get("/v1/consent").json()) == 1


def test_users_are_isolated(client_for):
    c1 = client_for("user-1")
    c1.post("/v1/memory", json={"content": "u1 secret"})
    c1.post("/v1/mood", json={"mood": 3})

    c2 = client_for("user-2")
    assert c2.get("/v1/memory").json()["items"] == []
    assert c2.get("/v1/mood/trends").json()["points"] == []

    # and user-1 still sees their own data after user-2 exists
    assert len(c1.get("/v1/memory").json()["items"]) == 1