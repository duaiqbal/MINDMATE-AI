"""Crisis detection + fixed response routing.

Hard rules enforced here:
  * The crisis path returns a FIXED, pre-written response. The LLM is NEVER
    called on this path (this module does not import app.llm at all).
  * Helplines are read from the crisis_resources table/rows passed in; nothing
    is hard-coded or invented.

Detection uses the human-authored lexicon (empty in the skeleton). With an
empty lexicon, is_crisis is always False — the system fails safe by not
fabricating crisis matches.
"""

from __future__ import annotations

from app.safety.lexicon import load_crisis_lexicon
from app.safety.models import CrisisCheck, CrisisResource

# The fixed response TEMPLATE structure. The specific supportive wording is
# intentionally minimal and human-reviewable; helpline details are injected
# from the database rows, never hard-coded.
_FIXED_RESPONSE_PREFIX = {
    "en": "You matter, and you deserve support right now. If you are in immediate danger, please reach out to a trained person who can help:",  # noqa: E501
    "roman_ur": "Aap ahem hain, aur is waqt aap ko madad milni chahiye. Agar aap fori khatre mein hain to kisi tarbiyat-yafta shakhs se rabta karein:",  # noqa: E501
}


def check_crisis(normalized_text: str) -> CrisisCheck:
    """Check text against the human-authored lexicon. Empty lexicon -> no match."""
    entries, version = load_crisis_lexicon()
    matched = [e.phrase for e in entries if e.phrase and e.phrase in normalized_text]
    return CrisisCheck(is_crisis=bool(matched), matched=matched, lexicon_version=version)


def build_fixed_response(
    resources: list[CrisisResource], language: str = "en"
) -> str:
    """Build the fixed crisis response from DB-provided resources.

    The LLM is NOT involved. If no resources are provided, only the supportive
    prefix is returned (no invented numbers).
    """
    prefix = _FIXED_RESPONSE_PREFIX.get(language, _FIXED_RESPONSE_PREFIX["en"])
    lines = [prefix]
    for r in resources:
        parts = [r.name]
        if r.phone:
            parts.append(r.phone)
        if r.url:
            parts.append(r.url)
        lines.append(" — ".join(parts))
    return "\n".join(lines)
