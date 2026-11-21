"""CORS: only configured frontend origins may call the API from a browser."""

from fastapi.testclient import TestClient

from app.config import CorsSettings
from app.main import create_app

ALLOWED = "http://localhost:5173"


def _preflight(client: TestClient, origin: str):
    return client.options(
        "/v1/chat",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_allowed_origin_gets_cors_headers():
    client = TestClient(create_app(CorsSettings(cors_allow_origins=ALLOWED)))
    r = _preflight(client, ALLOWED)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ALLOWED


def test_unknown_origin_is_not_allowed():
    client = TestClient(create_app(CorsSettings(cors_allow_origins=ALLOWED)))
    r = _preflight(client, "https://evil.example")
    assert "access-control-allow-origin" not in r.headers


def test_actual_chat_request_carries_cors_header():
    client = TestClient(create_app(CorsSettings(cors_allow_origins=ALLOWED)))
    r = client.post("/v1/chat", json={"message": "hi"}, headers={"Origin": ALLOWED})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ALLOWED


def test_origins_are_parsed_from_comma_list():
    s = CorsSettings(cors_allow_origins=" http://a.test , http://b.test ,")
    assert s.origins() == ["http://a.test", "http://b.test"]