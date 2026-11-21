"""Roman Urdu text normalizer.

Rule-based, deterministic, and versioned (reproducibility: every analysis logs
NORMALIZER_VERSION). No external data or model is required.

Scope (Phase 1): surface normalization only. It does NOT translate, detect
language, or change meaning. It:
  * lowercases,
  * normalizes unicode (NFKC),
  * collapses repeated characters (elongation): "yaaaar" -> "yaar",
  * collapses whitespace,
  * strips most punctuation but keeps intra-word apostrophes,
  * maps a SMALL, conservative table of common Roman Urdu spelling variants
    to a single canonical form.

The variant table is intentionally tiny and conservative; a human-reviewed
lexicon expands it later. Nothing here is invented domain content.
"""

from __future__ import annotations

import re
import unicodedata

NORMALIZER_VERSION = "roman_ur-normalizer-0.1.0"

# Conservative canonical spellings for extremely common tokens. Kept small on
# purpose; the reviewed lexicon is the real source later.
_VARIANTS: dict[str, str] = {
    "q": "kyun",
    "kiun": "kyun",
    "kyu": "kyun",
    "kyun": "kyun",
    "nai": "nahi",
    "nhi": "nahi",
    "nahin": "nahi",
    "hy": "hai",
    "hai": "hai",
    "mjhe": "mujhe",
    "mujhay": "mujhe",
    "acha": "acha",
    "accha": "acha",
    "theek": "theek",
    "thk": "theek",
}

# Characters that commonly get elongated for emphasis.
_ELONGATION_RE = re.compile(r"(.)\1{2,}", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+", re.UNICODE)
# Keep letters, digits, whitespace and intra-word apostrophes; drop the rest.
_PUNCT_RE = re.compile(r"[^\w\s']", re.UNICODE)


def _collapse_elongation(token: str) -> str:
    """Reduce a run of 3+ identical chars to 2 ("yaaaar" -> "yaar").

    Two is kept (not one) to avoid destroying legitimate double letters.
    """
    return _ELONGATION_RE.sub(r"\1\1", token)


def normalize(text: str) -> str:
    """Return the normalized Roman Urdu form of ``text``.

    Deterministic and side-effect free. Empty/whitespace input returns "".
    """
    if not text:
        return ""

    # Unicode normalize + lowercase.
    text = unicodedata.normalize("NFKC", text).lower()

    # Remove punctuation (keeps apostrophes), collapse whitespace.
    text = _PUNCT_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if not text:
        return ""

    out: list[str] = []
    for token in text.split(" "):
        token = _collapse_elongation(token)
        token = _VARIANTS.get(token, token)
        out.append(token)
    return " ".join(out)