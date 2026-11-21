"""End-to-end chat pipeline tests (no real model / no real LLM provider)."""

from app.chat import respond
from app.chat.orchestrator import ChatResult
from app.llm.gateway import GatewayConfig, LlmGateway


def _gateway(reply: str) -> LlmGateway:
    return LlmGateway(GatewayConfig(model_name="test"), lambda model, p: reply)


def test_pipeline_returns_result_without_gateway_uses_fallback():
    # No gateway + no emotion model -> safe template, never a crash.
    res = respond("I had a long day")
    assert isinstance(res, ChatResult)
    assert res.reply  # non-empty safe reply
    assert res.used_fallback is True
    # emotion model is absent in the skeleton -> low confidence -> clarify
    assert res.strategy == "clarify"
    assert res.is_crisis is False


def test_pipeline_passes_valid_llm_reply_through():
    gw = _gateway("That sounds heavy. What part felt hardest today?")
    res = respond("I feel low", gateway=gw)
    assert res.reply == "That sounds heavy. What part felt hardest today?"
    assert res.used_fallback is False


def test_pipeline_blocks_diagnosis_from_llm():
    # If the model returns a forbidden diagnosis, the validator must replace it.
    gw = _gateway("You have depression and need medication.")
    res = respond("I feel low", gateway=gw)
    assert "depression" not in res.reply.lower()
    assert res.used_fallback is True


def test_pipeline_records_provenance_versions():
    res = respond("hello", gateway=_gateway("Hi, how are you feeling?"))
    p = res.provenance
    for key in (
        "normalizer_version",
        "lang_id_version",
        "persona_version",
        "rule_table_version",
        "threshold_version",
        "model_version",
    ):
        assert key in p


def test_pipeline_language_detection_roman_urdu():
    res = respond("mujhe aaj acha nahi lag raha", gateway=_gateway("Main sun raha hoon."))
    assert res.language == "roman_ur"