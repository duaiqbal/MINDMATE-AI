"""Rule-based nuance tagger for self-discovery (no model/data required).

Given a core emotion (from the model) + the user text, it surfaces finer
feelings ("nuances") by matching human-authored markers from
config/emotion_taxonomy.yaml. Nuances are offered as GENTLE POSSIBILITIES,
never facts or diagnoses. Deterministic and versioned; missing taxonomy -> no
nuances (fails safe).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_CONFIG = Path(__file__).resolve().parents[2] / "config" / "emotion_taxonomy.yaml"


@dataclass(frozen=True)
class NuanceResult:
    core: str
    nuances: list[str] = field(default_factory=list)
    taxonomy_version: str = "unset"


def _load() -> dict:
    if not _CONFIG.exists():
        return {}
    return yaml.safe_load(_CONFIG.read_text(encoding="utf-8")) or {}


def _contains_marker(text: str, marker: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", text) is not None


def tag_nuances(core: str, text: str, language: str = "en") -> NuanceResult:
    """Return nuances under ``core`` whose markers appear in ``text``."""
    doc = _load()
    version = doc.get("version", "taxonomy-missing")
    core_node = (doc.get("core") or {}).get(core)
    if not core_node:
        return NuanceResult(core=core, nuances=[], taxonomy_version=version)

    low = text.lower()
    found: list[str] = []
    for nuance_name, langs in (core_node.get("nuances") or {}).items():
        markers = (langs or {}).get(language) or []
        if any(_contains_marker(low, m.lower()) for m in markers):
            found.append(nuance_name)
    return NuanceResult(core=core, nuances=found, taxonomy_version=version)