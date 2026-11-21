"""Conversation-history pattern detection (self-discovery).

Notices when a topic the USER themselves mentioned keeps appearing together
with a difficult feeling across several turns. Rules (product.md):

* Insights are QUESTIONS, hedged, and correctable ("or am I off?").
* Evidence is always shown (the user's own words).
* No cause is asserted: we only say two things came up together.
* No condition labels, no diagnosis.
* At least ``min_evidence`` distinct turns are required; otherwise nothing.
* A dismissed insight (user said "that's wrong") is never shown again.

Deterministic and versioned. Missing config -> no insights (fails safe).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PATTERNS_VERSION = "patterns-0.1.0"

_CONFIG = Path(__file__).resolve().parents[2] / "config" / "pattern_topics.yaml"

# Only difficult feelings form a pattern worth reflecting on.
DIFFICULT = ("sadness", "fear_anxiety", "anger")

_FEELING = {
    "en": {
        "sadness": "low",
        "fear_anxiety": "worried",
        "anger": "frustrated",
    },
    "roman_ur": {
        "sadness": "udaas",
        "fear_anxiety": "pareshan",
        "anger": "gusse mein",
    },
}

_TEMPLATE = {
    "en": (
        "I've noticed {topic} came up more than once when you felt {feeling}. "
        "Does that match how it feels to you, or am I off?"
    ),
    "roman_ur": (
        "Maine notice kiya ke jab aap {feeling} the, to {topic} ka zikr "
        "ek se zyada baar aaya. Kya ye aap ko theek lagta hai, ya main "
        "ghalat samajh raha hoon?"
    ),
}


@dataclass(frozen=True)
class Turn:
    """One past user message with its detected emotion."""

    text: str
    emotion: str | None
    language: str = "en"


@dataclass(frozen=True)
class Insight:
    key: str  # "<topic>:<emotion>", used for user corrections
    topic: str
    emotion: str
    turn_indices: list[int]
    evidence: list[str]  # the user's own words, shown with the insight
    question: str
    config_version: str = "unset"
    patterns_version: str = PATTERNS_VERSION
    sources: list[str] = field(default_factory=list)


def _load() -> dict:
    if not _CONFIG.exists():
        return {}
    return yaml.safe_load(_CONFIG.read_text(encoding="utf-8")) or {}


def _has(text: str, marker: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text) is not None


def _snippet(text: str, limit: int = 80) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def detect_patterns(
    history: list[Turn],
    *,
    language: str = "en",
    min_evidence: int = 2,
    max_insights: int = 2,
    dismissed: frozenset[str] | set[str] = frozenset(),
) -> list[Insight]:
    """Return hedged, evidence-backed insights from past turns."""
    doc = _load()
    if not doc:
        return []
    version = doc.get("version", "unset")
    topics = doc.get("topics") or {}
    out_lang = language if language in _TEMPLATE else "en"

    found: list[Insight] = []
    for topic, node in topics.items():
        for emotion in DIFFICULT:
            key = f"{topic}:{emotion}"
            if key in dismissed:
                continue
            idx: list[int] = []
            for i, turn in enumerate(history):
                if turn.emotion != emotion:
                    continue
                lang = turn.language if turn.language in ("en", "roman_ur") else "en"
                markers = (node.get("markers") or {}).get(lang) or []
                low = turn.text.lower()
                if any(_has(low, m.lower()) for m in markers):
                    idx.append(i)
            if len(idx) < min_evidence:
                continue
            label = (node.get("label") or {}).get(out_lang, topic)
            question = _TEMPLATE[out_lang].format(
                topic=label, feeling=_FEELING[out_lang][emotion]
            )
            found.append(
                Insight(
                    key=key,
                    topic=topic,
                    emotion=emotion,
                    turn_indices=idx,
                    evidence=[_snippet(history[i].text) for i in idx],
                    question=question,
                    config_version=version,
                )
            )

    found.sort(key=lambda ins: (-len(ins.turn_indices), ins.key))
    return found[:max_insights]