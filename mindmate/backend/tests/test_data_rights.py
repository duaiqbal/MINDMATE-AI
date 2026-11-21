"""Tests for export + account-delete (data-rights)."""

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user_id, get_repository
from app.db.repository import InMemoryRepository
from app.main import create_app


@pytest.fixture
def client_for():
    repo = InMemoryRepository()

    def _make(user_id: str) -> TestClient:
        app = create_app()
        app.dependency_overrides[get_repository] = lambda: repo
        app.dependency_overrides[get_current_user_id] = lambda: user_id
        return TestClient(app)

    return _make


def test_export_returns_all_user_data(client_for):
    c = client_for("user-1")
    c.post("/v1/mood", json={"mood": 5})
    c.post("/v1/memory", json={"content": "note"})
    c.post("/v1/consent", json={"consent_type": "data_processing"})

    exported = c.get("/v1/export").json()
    assert exported["user_id"] == "user-1"
    assert len(exported["moods"]) == 1
    assert len(exported["memory"]) == 1
    assert len(exported["consents"]) == 1


def test_export_only_includes_own_data(client_for):
    c1 = client_for("user-1")
    c1.post("/v1/memory", json={"content": "u1"})
    c2 = client_for("user-2")
    assert c2.get("/v1/export").json()["memory"] == []


def test_delete_account_removes_all_data(client_for):
    c = client_for("user-1")
    c.post("/v1/mood", json={"mood": 3})
    c.post("/v1/memory", json={"content": "x"})

    assert c.delete("/v1/account").status_code == 204

    exported = c.get("/v1/export").json()
    assert exported["moods"] == []
    assert exported["memory"] == []
    assert exported["consents"] == []


def test_delete_account_does_not_touch_other_users(client_for):
    c1 = client_for("user-1")
    c1.post("/v1/memory", json={"content": "keep me"})
    c2 = client_for("user-2")
    c2.post("/v1/memory", json={"content": "delete me"})

    c2.delete("/v1/account")

    assert len(c1.get("/v1/export").json()["memory"]) == 1