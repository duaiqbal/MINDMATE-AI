"""Validate the processed emotion datasets (skipped if not generated locally).

Checks: every row passes the backend schema, languages are separate, the test
split matches its frozen hash, and no text appears in both train and test.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.emotion import LABELS
from app.emotion.dataset import load_dataset

PROCESSED = Path(__file__).resolve().parents[2] / "ml" / "data" / "processed"
STATS = PROCESSED / "stats.json"

pytestmark = pytest.mark.skipif(
    not (PROCESSED / "emotion_en.jsonl").exists(),
    reason="processed datasets not generated (run ml/data/prepare_datasets.py)",
)


@pytest.fixture(scope="module")
def stats():
    return json.loads(STATS.read_text(encoding="utf-8"))


@pytest.mark.parametrize("lang", ["en", "roman_ur"])
def test_rows_pass_schema_and_stay_in_language(lang):
    samples = load_dataset(PROCESSED / f"emotion_{lang}.jsonl")
    assert samples
    assert {s.language for s in samples} == {lang}
    assert {s.label for s in samples} <= set(LABELS)


@pytest.mark.parametrize("lang", ["en", "roman_ur"])
def test_frozen_test_split_hash_unchanged(lang, stats):
    data = (PROCESSED / f"emotion_{lang}.test.FROZEN.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == stats[lang]["sha256_test_frozen"]


@pytest.mark.parametrize("lang", ["en", "roman_ur"])
def test_no_train_test_overlap(lang):
    samples = load_dataset(PROCESSED / f"emotion_{lang}.jsonl")

    def key(t: str) -> str:
        return " ".join(t.lower().split())

    train = {key(s.text) for s in samples if s.split == "train"}
    test = {key(s.text) for s in samples if s.split == "test"}
    overlap = train & test
    # roman_ur is hash-split on normalized text, so overlap must be zero.
    # GoEmotions keeps its official splits; tiny duplicates there are allowed
    # but must stay under 1% of the test set.
    limit = 0 if lang == "roman_ur" else len(test) // 100
    assert len(overlap) <= limit