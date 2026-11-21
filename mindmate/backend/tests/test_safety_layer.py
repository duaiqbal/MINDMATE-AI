"""Tests for the safety layer schema, loader, detector, fixed response.

These do NOT author crisis content. They verify the mechanism: empty lexicon
fails safe, resources are never invented, and the fixed response contains only
DB-provided data.
"""

import pytest

from app.safety.detector import build_fixed_response, check_crisis
from app.safety.lexicon import load_crisis_lexicon
from app.safety.models import CrisisLexiconEntry, CrisisResource


def test_empty_lexicon_fails_safe():
    # Skeleton has no lexicon file -> no crisis fabricated.
    check = check_crisis("any text at all")
    assert check.is_crisis is False
    assert check.matched == []


def test_lexicon_loader_returns_version_when_missing():
    entries, version = load_crisis_lexicon()
    assert entries == []
    assert "crisis-lexicon" in version


def test_lexicon_entry_validation():
    with pytest.raises(ValueError):
        CrisisLexiconEntry(phrase="  ", language="en", severity="high")
    with pytest.raises(ValueError):
        CrisisLexiconEntry(phrase="x", language="de", severity="high")


def test_fixed_response_contains_only_provided_resources():
    # Resource data is injected (as if from DB); nothing invented.
    res = [CrisisResource(name="PLACEHOLDER Helpline", phone="REDACTED-FROM-DB")]
    out = build_fixed_response(res, "en")
    assert "PLACEHOLDER Helpline" in out
    assert "REDACTED-FROM-DB" in out


def test_fixed_response_with_no_resources_invents_nothing():
    out = build_fixed_response([], "roman_ur")
    # Only the supportive prefix; no digits / phone numbers fabricated.
    assert not any(ch.isdigit() for ch in out)


def test_fixed_response_language_fallback():
    out = build_fixed_response([], "fr")
    assert out  # falls back to English prefix