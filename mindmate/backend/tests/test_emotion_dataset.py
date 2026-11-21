"""Tests for emotion dataset loader + schema validation (no real dataset)."""

from pathlib import Path

import pytest

from app.emotion.dataset import Sample, load_dataset, per_language_counts


def test_sample_validation():
    Sample(text="I feel great", label="joy", language="en", split="train")
    with pytest.raises(ValueError):
        Sample(text="", label="joy", language="en")
    with pytest.raises(ValueError):
        Sample(text="x", label="depression", language="en")  # not a valid label
    with pytest.raises(ValueError):
        Sample(text="x", label="joy", language="fr")
    with pytest.raises(ValueError):
        Sample(text="x", label="joy", language="en", split="holdout")


def test_load_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "nope.csv")


def test_load_csv_roundtrip(tmp_path: Path):
    p = tmp_path / "d.csv"
    p.write_text(
        "text,label,language,source,split\n"
        "I am happy,joy,en,annotated,train\n"
        "mujhe dar lag raha hai,fear_anxiety,roman_ur,annotated,val\n",
        encoding="utf-8",
    )
    samples = load_dataset(p)
    assert len(samples) == 2
    counts = per_language_counts(samples)
    assert counts["en"]["joy"] == 1
    assert counts["roman_ur"]["fear_anxiety"] == 1
    # languages stay separate (never pooled); en and roman_ur are distinct
    assert counts["en"]["fear_anxiety"] == 0
    assert counts["roman_ur"]["joy"] == 0


def test_load_rejects_bad_row(tmp_path: Path):
    p = tmp_path / "bad.csv"
    p.write_text(
        "text,label,language\nhello,not_a_label,en\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        load_dataset(p)