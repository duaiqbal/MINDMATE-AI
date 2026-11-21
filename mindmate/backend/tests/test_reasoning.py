"""Tests for the reasoning engine + uncertainty gate (data-driven strategy)."""

import pytest

from app.reasoning import ReasoningInput, load_engine


@pytest.fixture(scope="module")
def engine():
    return load_engine()


def test_crisis_overrides_everything(engine):
    # Even with high confidence + positive emotion, crisis wins.
    d = engine.decide(ReasoningInput(emotion="joy", confidence=0.99, crisis=True))
    assert d.strategy == "crisis_response"
    assert d.matched_rule == "crisis_overrides_everything"


def test_low_confidence_clarifies(engine):
    d = engine.decide(ReasoningInput(emotion="sadness", confidence=0.10))
    assert d.strategy == "clarify"
    assert d.matched_rule == "low_confidence_clarifies"


def test_confident_distress_reflects(engine):
    for emo in ("sadness", "fear_anxiety", "anger"):
        d = engine.decide(ReasoningInput(emotion=emo, confidence=0.95))
        assert d.strategy == "reflect", emo


def test_confident_positive_supports(engine):
    for emo in ("joy", "neutral"):
        d = engine.decide(ReasoningInput(emotion=emo, confidence=0.95))
        assert d.strategy == "support", emo


def test_confidence_exactly_at_threshold_is_not_low(engine):
    # threshold is 0.55; strictly-below triggers clarify, so 0.55 does NOT.
    d = engine.decide(ReasoningInput(emotion="anger", confidence=0.55))
    assert d.strategy == "reflect"


def test_decision_carries_provenance(engine):
    d = engine.decide(ReasoningInput(emotion="joy", confidence=0.9))
    assert d.rule_table_version.startswith("reasoning-rules-")
    assert d.threshold_version.startswith("thresholds-")
    assert "clarify" in d.thresholds_used


def test_invalid_emotion_rejected():
    with pytest.raises(ValueError):
        ReasoningInput(emotion="depressed", confidence=0.5)


def test_confidence_range_enforced():
    with pytest.raises(ValueError):
        ReasoningInput(emotion="joy", confidence=1.5)