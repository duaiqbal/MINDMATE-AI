"""Tests for the Roman Urdu normalizer (deterministic, no data needed)."""

from app.language.normalizer import NORMALIZER_VERSION, normalize


def test_empty_and_whitespace():
    assert normalize("") == ""
    assert normalize("   ") == ""


def test_lowercases_and_trims():
    assert normalize("  HELLO  ") == "hello"


def test_collapses_elongation():
    assert normalize("yaaaar") == "yaar"
    assert normalize("nooooo") == "noo"  # 3+ -> 2, meaning preserved loosely


def test_keeps_legitimate_double_letters():
    # two identical chars are NOT reduced
    assert normalize("accha") == "acha"  # via variant map, not elongation
    assert normalize("munna") == "munna"


def test_strips_punctuation_keeps_apostrophe():
    assert normalize("kya, haal hai?") == "kya haal hai"
    assert normalize("it's") == "it's"


def test_variant_mapping():
    assert normalize("nhi") == "nahi"
    assert normalize("q") == "kyun"
    assert normalize("thk") == "theek"


def test_sentence():
    assert normalize("Mjhe nhi pataaa!!!") == "mujhe nahi pataa"  # 3+ a -> 2


def test_is_deterministic():
    s = "Kiun  ACHA   hy??"
    assert normalize(s) == normalize(s)


def test_version_constant_present():
    assert NORMALIZER_VERSION.startswith("roman_ur-normalizer-")