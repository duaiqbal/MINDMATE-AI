"""Tests for the LLM gateway + PII masking (no real provider/network)."""

import pytest

from app.llm import GatewayConfig, LlmError, LlmGateway
from app.llm.pii import mask_pii


def test_mask_pii_email_phone_url():
    masked = mask_pii("mail me at a.b@x.com or +92 300 1234567 see http://x.io/p")
    assert "a.b@x.com" not in masked
    assert "[EMAIL]" in masked
    assert "[URL]" in masked
    assert "[PHONE]" in masked


def test_gateway_passes_only_masked_text_to_provider():
    seen = {}

    def provider(model, prompt):
        seen["model"] = model
        seen["prompt"] = prompt
        return "ok"

    gw = LlmGateway(GatewayConfig(model_name="m1"), provider)
    gw.complete("call me at test@example.com")
    assert seen["model"] == "m1"
    assert "test@example.com" not in seen["prompt"]
    assert "[EMAIL]" in seen["prompt"]


def test_gateway_returns_provider_reply():
    gw = LlmGateway(GatewayConfig(model_name="m"), lambda model, p: "hello")
    assert gw.complete("hi") == "hello"


def test_gateway_retries_then_succeeds():
    calls = {"n": 0}

    def flaky(model, prompt):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("transient")
        return "recovered"

    gw = LlmGateway(
        GatewayConfig(model_name="m", max_retries=2),
        flaky,
        sleep=lambda s: None,  # no real waiting in tests
    )
    assert gw.complete("x") == "recovered"
    assert calls["n"] == 2


def test_gateway_raises_after_exhausting_retries():
    def always_fail(model, prompt):
        raise RuntimeError("down")

    gw = LlmGateway(
        GatewayConfig(model_name="m", max_retries=1),
        always_fail,
        sleep=lambda s: None,
    )
    with pytest.raises(LlmError):
        gw.complete("x")