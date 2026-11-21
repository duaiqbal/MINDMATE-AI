"""Loader for the human-authored crisis lexicon.

Code provides ONLY the loader + schema + version. The actual phrases live in a
reviewed data file (JSON) that humans author. If the file is absent or empty
(as in this skeleton), the loader returns an empty lexicon with its version —
it never invents entries.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.safety.models import CrisisLexiconEntry

_LEXICON_DIR = Path(__file__).resolve().parents[2] / "lexicons"
_CRISIS_FILE = _LEXICON_DIR / "crisis_lexicon.json"


def load_crisis_lexicon(path: Path | None = None) -> tuple[list[CrisisLexiconEntry], str]:
    """Load crisis lexicon entries + version.

    Returns ([], version) if the file does not exist. Expected JSON shape:
        {"version": "...", "entries": [{"phrase": "...", "language": "en",
                                         "severity": "high"}, ...]}
    """
    path = path or _CRISIS_FILE
    if not path.exists():
        return [], "crisis-lexicon-missing"
    doc = json.loads(path.read_text(encoding="utf-8"))
    version = doc.get("version", "crisis-lexicon-unversioned")
    entries = [
        CrisisLexiconEntry(
            phrase=e["phrase"], language=e["language"], severity=e["severity"]
        )
        for e in doc.get("entries", [])
    ]
    return entries, version