"""Tests for the rule-based nuance tagger (self-discovery, no model needed)."""

from app.emotion.nuance import tag_nuances


def test_detects_loneliness_under_sadness_en():
    r = tag_nuances("sadness", "I feel so lonely and alone tonight", "en")
    assert "loneliness" in r.nuances
    assert r.core == "sadness"
    assert r.taxonomy_version.startswith("emotion-taxonomy-")


def test_detects_nuance_roman_urdu():
    r = tag_nuances("sadness", "main bohat tanha mehsoos kar raha hoon", "roman_ur")
    assert "loneliness" in r.nuances


def test_multiple_nuances_can_match():
    r = tag_nuances("fear_anxiety", "I am worried and totally overwhelmed", "en")
    assert "worry" in r.nuances
    assert "overwhelm" in r.nuances


def test_no_false_match_without_markers():
    r = tag_nuances("joy", "the weather is nice today", "en")
    assert r.nuances == []


def test_marker_respects_word_boundary():
    # "alone" should not be matched inside "malone"
    r = tag_nuances("sadness", "malone is a surname", "en")
    assert "loneliness" not in r.nuances


def test_unknown_core_returns_empty():
    r = tag_nuances("not_a_core", "lonely", "en")
    assert r.nuances == []