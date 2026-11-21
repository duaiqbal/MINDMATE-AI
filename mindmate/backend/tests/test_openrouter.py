"""OpenRouter provider + gateway wiring (no network: httpx.MockTransport)."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.chat import get_gateway
from app.chat import respond
from app.llm.gateway import GatewayConfig, LlmError, LlmGateway
from app.llm.openrouter import ProviderError, make_openrouter_provider
from app.main import create_app

KEY = "sk-or-v1-test-key-not-real"
BASE = "https://openrouter.test/api/v1"


def _ok(content="That sounds hard. What happened today?"):
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def _provider(handler):
    return make_openrouter_provider(
        api_key=KEY,
        base_url=BASE,
        timeout_seconds=5,
        transport=httpx.MockTransport(handler),
    )


def test_request_shape_auth_privacy_and_no_tools():
    seen = {}

    def handler(request: httpx.Request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=_ok())

    reply = _provider(handler)("google/gemma-4-31b-it:free", "hello")
    assert reply == "That sounds hard. What happened today?"
    assert seen["url"] == f"{BASE}/chat/completions"
    assert seen["auth"] == f"Bearer {KEY}"
    body = seen["body"]
    assert body["model"] == "google/gemma-4-31b-it:free"
    assert body["messages"] == [{"role": "user", "content": "hello"}]
    assert body["provider"] == {"data_collection": "deny"}
    assert "tools" not in body and "tool_choice" not in body


@pytest.mark.parametrize("status", [401, 429, 500])
def test_http_error_raises_without_leaking_key(status):
    p = _provider(lambda r: httpx.Response(status, json={"error": {"message": "x"}}))
    with pytest.raises(ProviderError) as exc:
        p("m", "hi")
    assert str(status) in str(exc.value)
    assert KEY not in str(exc.value)


@pytest.mark.parametrize(
    "payload",
    [{"choices": []}, {"choices": [{"message": {"content": "   "}}]}, {"nope": 1}],
)
def test_unusable_response_raises(payload):
    p = _provider(lambda r: httpx.Response(200, json=payload))
    with pytest.raises(ProviderError):
        p("m", "hi")


def test_gateway_sends_only_masked_text_over_http():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=_ok("ok"))

    gw = LlmGateway(GatewayConfig(model_name="m"), _provider(handler))
    gw.complete("email me at ali@example.com")
    text = seen["body"]["messages"][0]["content"]
    assert "ali@example.com" not in text
    assert "[EMAIL]" in text


def test_gateway_gives_up_after_retries():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(503)

    gw = LlmGateway(
        GatewayConfig(model_name="m", max_retries=2), _provider(handler), sleep=lambda s: None
    )
    with pytest.raises(LlmError):
        gw.complete("hi")
    assert calls["n"] == 3


def test_get_gateway_is_none_without_key():
    assert get_gateway() is None  # conftest blanks the key


def test_get_gateway_uses_configured_model(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    monkeypatch.setenv("LLM_MODEL_NAME", "google/gemma-4-26b-a4b-it:free")
    gw = get_gateway()
    assert isinstance(gw, LlmGateway)
    assert gw.model_name == "google/gemma-4-26b-a4b-it:free"


def test_provider_failure_falls_back_to_template_and_logs_model():
    gw = LlmGateway(
        GatewayConfig(model_name="m-test", max_retries=1),
        _provider(lambda r: httpx.Response(500)),
        sleep=lambda s: None,
    )
    res = respond("I feel low", gateway=gw)
    assert res.used_fallback is True
    assert res.reply  # safe template, never empty
    assert res.provenance["llm_model"] == "m-test"


def test_endpoint_uses_real_provider_reply():
    reply = "I'm here for you. What's on your mind?"
    gw = LlmGateway(
        GatewayConfig(model_name="m"),
        _provider(lambda r: httpx.Response(200, json=_ok(reply))),
    )
    app = create_app()
    app.dependency_overrides[get_gateway] = lambda: gw
    r = TestClient(app).post("/v1/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json()["reply"] == reply
    assert r.json()["used_fallback"] is False