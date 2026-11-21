"""Tests for conversation-history pattern detection (hedged, evidence-based)."""

from app.longitudinal.patterns import Turn, detect_patterns
from app.validator import validate_reply


def _hist_en():
    return [
        Turn("My boss gave me another deadline", "fear_anxiety", "en"),
        Turn("Nice weather today", "joy", "en"),
        Turn("Work is getting heavy again", "fear_anxiety", "en"),
    ]


def test_no_insight_with_single_turn():
    hist = [Turn("My boss gave me a deadline", "fear_anxiety", "en")]
    assert detect_patterns(hist) == []


def test_insight_when_topic_repeats_with_difficult_feeling():
    out = detect_patterns(_hist_en())
    assert len(out) == 1
    ins = out[0]
    assert ins.topic == "work"
    assert ins.emotion == "fear_anxiety"
    assert ins.turn_indices == [0, 2]


def test_insight_is_a_hedged_correctable_question():
    q = detect_patterns(_hist_en())[0].question
    assert q.endswith("?")
    assert "or am I off" in q


def test_insight_shows_users_own_words_as_evidence():
    ins = detect_patterns(_hist_en())[0]
    assert "My boss gave me another deadline" in ins.evidence[0]
    assert len(ins.evidence) == len(ins.turn_indices)


def test_positive_feelings_never_form_a_pattern():
    hist = [
        Turn("Work went great", "joy", "en"),
        Turn("My job is fun", "joy", "en"),
    ]
    assert detect_patterns(hist) == []


def test_dismissed_insight_is_not_shown_again():
    first = detect_patterns(_hist_en())[0]
    again = detect_patterns(_hist_en(), dismissed={first.key})
    assert again == []


def test_insight_text_passes_the_output_validator():
    for lang in ("en", "roman_ur"):
        q = detect_patterns(_hist_en(), language=lang)[0].question
        assert validate_reply(q).ok


def test_roman_urdu_history_and_reply_language():
    hist = [
        Turn("boss ne phir deadline di", "fear_anxiety", "roman_ur"),
        Turn("aaj kaam bohat zyada tha", "fear_anxiety", "roman_ur"),
    ]
    ins = detect_patterns(hist, language="roman_ur")[0]
    assert "pareshan" in ins.question
    assert "kaam" in ins.question


def test_no_cause_or_condition_claim_in_text():
    q = detect_patterns(_hist_en())[0].question.lower()
    for banned in ("because", "caused", "disorder", "depress", "diagnos"):
        assert banned not in q


def test_max_insights_is_capped():
    hist = [
        Turn("work and exam stress", "fear_anxiety", "en"),
        Turn("work and exam again", "fear_anxiety", "en"),
        Turn("my family and friends fight", "anger", "en"),
        Turn("family and friends again", "anger", "en"),
        Turn("money and sleep trouble", "sadness", "en"),
        Turn("money and sleep again", "sadness", "en"),
    ]
    assert len(detect_patterns(hist, max_insights=2)) <= 2