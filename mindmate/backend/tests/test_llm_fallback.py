"""Model fallback chain in the OpenRouter provider (no network)."""

import json

import httpx
import pytest

from app.api.chat import get_gateway
from app.chat import respond
from app.config import LlmSettings
from app.llm.gateway import GatewayConfig, LlmGateway
from app.llm.openrouter import ProviderError, make_openrouter_provider

KEY = "sk-or-v1-test-key-not-real"


def _chain_provider(status_by_model: dict[str, int], seen: list[str]):
    def handler(request: httpx.Request):
        model = json.loads(request.content)["model"]
        seen.append(model)
        status = status_by_model.get(model, 200)
        if status == 200:
            return httpx.Response(
                200, json={"choices": [{"message": {"content": f"reply from {model}"}}]}
            )
        return httpx.Response(status, json={"error": {"message": "x"}})

    return make_openrouter_provider(
        api_key=KEY,
        base_url="https://openrouter.test/api/v1",
        timeout_seconds=5,
        fallback_models=["b", "c"],
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.parametrize("busy_status", [404, 429, 502, 503])
def test_busy_primary_falls_back_to_next_model(busy_status):
    seen: list[str] = []
    p = _chain_provider({"a": busy_status}, seen)
    assert p("a", "hi") == "reply from b"
    assert seen == ["a", "b"]
    assert p.last_model == "b"


def test_primary_used_when_available():
    seen: list[str] = []
    p = _chain_provider({}, seen)
    assert p("a", "hi") == "reply from a"
    assert seen == ["a"]
    assert p.last_model == "a"


@pytest.mark.parametrize("auth_status", [401, 402, 403])
def test_key_errors_do_not_fall_back(auth_status):
    seen: list[str] = []
    p = _chain_provider({"a": auth_status}, seen)
    with pytest.raises(ProviderError):
        p("a", "hi")
    assert seen == ["a"]  # no quota wasted on other models


def test_all_busy_raises_with_every_model_listed():
    seen: list[str] = []
    p = _chain_provider({"a": 429, "b": 429, "c": 404}, seen)
    with pytest.raises(ProviderError) as exc:
        p("a", "hi")
    assert seen == ["a", "b", "c"]
    assert "a: HTTP 429" in str(exc.value) and "c: HTTP 404" in str(exc.value)
    assert KEY not in str(exc.value)


def test_chain_skips_duplicate_of_primary():
    seen: list[str] = []
    p = make_openrouter_provider(
        api_key=KEY,
        base_url="https://openrouter.test/api/v1",
        timeout_seconds=5,
        fallback_models=["a", "b"],
        transport=httpx.MockTransport(
            lambda r: (
                seen.append(json.loads(r.content)["model"])
                or httpx.Response(429, json={})
            )
        ),
    )
    with pytest.raises(ProviderError):
        p("a", "hi")
    assert seen == ["a", "b"]


def test_settings_fallback_list_is_clean(monkeypatch):
    monkeypatch.setenv("LLM_MODEL_NAME", "a")
    monkeypatch.setenv("LLM_FALLBACK_MODELS", " b , a, ,b, c ")
    assert LlmSettings().fallbacks() == ["b", "c"]


def test_pipeline_logs_model_that_actually_answered():
    seen: list[str] = []
    gw = LlmGateway(
        GatewayConfig(model_name="a", max_retries=0), _chain_provider({"a": 429}, seen)
    )
    res = respond("I feel low", gateway=gw)
    assert res.used_fallback is False
    assert res.provenance["llm_model"] == "a"
    assert res.provenance["llm_model_used"] == "b"


def test_get_gateway_wires_fallbacks(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    monkeypatch.setenv("LLM_FALLBACK_MODELS", "x:free,y:free")
    gw = get_gateway()
    assert gw is not None
    assert gw.last_model_used is None  # nothing answered yet