"""Tests for the /v1/chat endpoint (uses safe-fallback gateway by default)."""

from fastapi.testclient import TestClient

from app.api.chat import get_gateway
from app.llm.gateway import GatewayConfig, LlmGateway
from app.main import create_app


def test_chat_endpoint_without_provider_returns_safe_reply():
    client = TestClient(create_app())
    r = client.post("/v1/chat", json={"message": "I had a rough day"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert body["used_fallback"] is True
    assert body["is_crisis"] is False
    assert "strategy" in body


def test_chat_endpoint_with_injected_gateway():
    app = create_app()
    gw = LlmGateway(GatewayConfig(model_name="t"), lambda m, p: "I'm here. What's on your mind?")
    app.dependency_overrides[get_gateway] = lambda: gw
    client = TestClient(app)
    r = client.post("/v1/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json()["reply"] == "I'm here. What's on your mind?"


def test_chat_endpoint_validates_empty_message():
    client = TestClient(create_app())
    assert client.post("/v1/chat", json={"message": ""}).status_code == 422