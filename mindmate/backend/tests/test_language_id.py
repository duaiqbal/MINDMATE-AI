"""Tests for rule-based language identification (no dataset needed)."""

from app.language.identifier import SUPPORTED, identify


def test_empty_is_low_confidence():
    r = identify("")
    assert r.confidence == 0.0
    r2 = identify("   ")
    assert r2.confidence == 0.0


def test_urdu_script_is_low_confidence_now():
    # Urdu script is no longer a supported output; it must NOT be served as a
    # confident language. Low confidence -> reasoning gate asks to clarify.
    r = identify("آپ کیسے ہیں")
    assert r.language in ("en", "roman_ur")
    assert r.confidence < 0.4


def test_clear_english():
    r = identify("I went to the office and finished my report today")
    assert r.language == "en"
    assert r.confidence >= 0.5


def test_roman_urdu_markers():
    r = identify("aap kaise hain mujhe acha nahi lag raha")
    assert r.language == "roman_ur"
    assert r.confidence > 0.6


def test_result_language_always_supported():
    for text in ["hello world", "kya haal hai", "آج موسم اچھا ہے", "", "12345"]:
        assert identify(text).language in SUPPORTED


def test_confidence_in_range():
    for text in ["hi", "mujhe nahi pata", "یہ ایک جملہ ہے", "random english text here"]:
        c = identify(text).confidence
        assert 0.0 <= c <= 1.0


def test_short_ambiguous_is_not_overconfident():
    # a single ambiguous word should not be high confidence
    r = identify("ok")
    assert r.confidence < 0.6


def test_carries_version():
    assert identify("hello").version.startswith("language-id-rules-")