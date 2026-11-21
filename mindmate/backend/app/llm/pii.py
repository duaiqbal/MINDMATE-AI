"""Minimal PII masking applied BEFORE any text reaches the gateway.

Conservative regex masking for the most common direct identifiers. This is a
safety reducer, not a guarantee; it intentionally over-masks. No external data.
"""

from __future__ import annotations

import re

PII_MASKER_VERSION = "pii-masker-0.1.0"

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# Phone-like: 7+ digits possibly with +, spaces, dashes, parens.
_PHONE_RE = re.compile(r"(?<!\w)(\+?\d[\d\s().-]{6,}\d)(?!\w)")
_URL_RE = re.compile(r"\bhttps?://\S+\b", re.IGNORECASE)


def mask_pii(text: str) -> str:
    """Return ``text`` with emails, phone-like runs, and URLs masked."""
    if not text:
        return ""
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _URL_RE.sub("[URL]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    return text