"""Tests for the output validator + template fallback (product hard-rules)."""

import pytest

from app.validator import validate_or_fallback, validate_reply

SAFE = [
    "It sounds like things feel heavy right now. What has today been like for you?",
    "I hear you. Would it help to talk about what is on your mind?",
    "Thanks for sharing that. How are you feeling about it now?",
]

DIAGNOSIS = [
    "You have depression and should see a doctor.",
    "This is anxiety disorder, clearly.",
    "You're bipolar, that's why you feel this way.",
]

MEDICATION = [
    "You should start taking antidepressants.",
    "Try some Xanax to calm down.",
    "I recommend you use medication for this.",
]

CAUSE = [
    "This is because of your trauma.",
    "You feel this way because of your childhood.",
    "The real reason is your divorce.",
]


@pytest.mark.parametrize("text", SAFE)
def test_safe_replies_pass(text):
    assert validate_reply(text).ok


@pytest.mark.parametrize("text", DIAGNOSIS)
def test_diagnosis_rejected(text):
    r = validate_reply(text)
    assert not r.ok
    assert "diagnosis" in r.violations


@pytest.mark.parametrize("text", MEDICATION)
def test_medication_rejected(text):
    r = validate_reply(text)
    assert not r.ok
    assert "medication" in r.violations


@pytest.mark.parametrize("text", CAUSE)
def test_unstated_cause_rejected(text):
    r = validate_reply(text)
    assert not r.ok
    assert "unstated_cause" in r.violations


def test_fallback_returns_safe_template_on_violation():
    out, result = validate_or_fallback("You have depression.", "roman_ur")
    assert not result.ok
    # fallback is a hedged question, not the original
    assert "depression" not in out.lower()
    assert "?" in out


def test_fallback_passes_through_safe_text():
    text = "How are you feeling right now?"
    out, result = validate_or_fallback(text, "en")
    assert result.ok
    assert out == text


def test_fallback_language_defaults_to_english():
    out, _ = validate_or_fallback("You are schizophrenic.", "fr")
    assert out  # some safe string returned