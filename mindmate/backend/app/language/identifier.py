"""Rule-based language identification for en / ur / roman_ur.

Deterministic, versioned, no external data or model. It carries a calibrated
confidence so the uncertainty gate can route low-confidence input to "clarify"
instead of guessing (see product.md).

Method:
  * If the text is majority Urdu-script (Arabic Unicode block), -> "ur".
  * Otherwise the text is Latin; distinguish English vs Roman Urdu using a
    small, conservative set of very common Roman Urdu function-word markers.

This is a pragmatic baseline, NOT a trained classifier. English and Roman Urdu
overlap, so confidence stays honest: ambiguous input yields low confidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LANG_ID_VERSION = "language-id-rules-0.1.0"

SUPPORTED = ("en", "roman_ur")

# Arabic/Urdu Unicode ranges (covers Urdu script letters + presentation forms).
_URDU_SCRIPT_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]"
)
_LATIN_WORD_RE = re.compile(r"[a-z']+", re.IGNORECASE)

# Very common Roman Urdu function words. Conservative on purpose. A reviewed
# lexicon can expand this later; it is not invented domain content, just
# everyday words.
_ROMAN_UR_MARKERS = {
    "hai", "hain", "ho", "hoon", "tha", "thi", "kya", "kyun", "nahi", "nhi",
    "mujhe", "mujhay", "mera", "meri", "tum", "aap", "hum", "acha", "theek",
    "bohat", "bahut", "kaise", "kaisa", "raha", "rahi", "ke", "ki", "ka",
    "aur", "lekin", "magar", "kuch", "sab", "yaar", "pata", "dil", "dard",
}


@dataclass(frozen=True)
class LangResult:
    """Language identification result with provenance."""

    language: str
    confidence: float
    version: str = LANG_ID_VERSION


def _urdu_ratio(text: str) -> float:
    urdu = len(_URDU_SCRIPT_RE.findall(text))
    letters = len([c for c in text if not c.isspace() and not c.isdigit()])
    return urdu / letters if letters else 0.0


def identify(text: str) -> LangResult:
    """Identify the language/script of ``text`` with a calibrated confidence."""
    if not text or not text.strip():
        return LangResult("en", 0.0)

    urdu_ratio = _urdu_ratio(text)
    # Urdu *script* is no longer a supported output language (we support en +
    # roman_ur only). If the text is mostly Urdu script we cannot serve it in a
    # supported language, so we return low confidence and default to "en"; the
    # reasoning gate turns low confidence into a "clarify" (ask the user to
    # write in English or Roman Urdu) rather than guessing.
    if urdu_ratio >= 0.4:
        return LangResult("en", 0.1)

    # Latin text: English vs Roman Urdu via marker density.
    words = [w.lower() for w in _LATIN_WORD_RE.findall(text)]
    if not words:
        return LangResult("en", 0.1)

    marker_hits = sum(1 for w in words if w in _ROMAN_UR_MARKERS)
    density = marker_hits / len(words)

    if marker_hits == 0:
        # No Roman Urdu markers -> likely English, but short text is uncertain.
        conf = 0.55 if len(words) >= 3 else 0.4
        return LangResult("en", conf)

    # Some markers present -> Roman Urdu; confidence scales with density.
    conf = min(0.5 + density * 1.5, 0.95)
    return LangResult("roman_ur", conf)