"""Dataset schema + loader + validation for the emotion model.

Reads CSV or JSONL with columns: text, label, language, source, split.
It VALIDATES rows against the fixed label/language sets and never invents data.
If the file is missing, it raises FileNotFoundError (there is no fake fallback).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from app.emotion import LABELS, LANGUAGES

VALID_SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class Sample:
    text: str
    label: str
    language: str
    source: str = "unknown"
    split: str = "train"

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("sample text is empty")
        if self.label not in LABELS:
            raise ValueError(f"invalid label: {self.label!r}")
        if self.language not in LANGUAGES:
            raise ValueError(f"invalid language: {self.language!r}")
        if self.split not in VALID_SPLITS:
            raise ValueError(f"invalid split: {self.split!r}")


def _rows_from_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _rows_from_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def load_dataset(path: Path) -> list[Sample]:
    """Load + validate a dataset file (.csv or .jsonl). Raises on bad rows."""
    if not path.exists():
        raise FileNotFoundError(f"dataset not found: {path}")
    rows = _rows_from_csv(path) if path.suffix == ".csv" else _rows_from_jsonl(path)
    samples = []
    for i, r in enumerate(rows):
        try:
            samples.append(
                Sample(
                    text=r["text"],
                    label=r["label"],
                    language=r["language"],
                    source=r.get("source", "unknown"),
                    split=r.get("split", "train"),
                )
            )
        except (KeyError, ValueError) as exc:
            raise ValueError(f"row {i}: {exc}") from exc
    return samples


def per_language_counts(samples: list[Sample]) -> dict[str, dict[str, int]]:
    """Return {language: {label: count}} — useful for reporting (never pooled)."""
    out: dict[str, dict[str, int]] = {lang: dict.fromkeys(LABELS, 0) for lang in LANGUAGES}
    for s in samples:
        out[s.language][s.label] += 1
    return out