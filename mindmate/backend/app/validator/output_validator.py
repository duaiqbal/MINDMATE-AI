"""Validate an LLM reply against MindMate's non-negotiable product rules.

A reply is REJECTED (and replaced by a safe template) if it appears to:
  * diagnose / label a condition ("you have depression", "this is anxiety
    disorder", ...),
  * give medication or treatment advice,
  * assert an unstated cause ("this is because of your trauma", ...).

This is a conservative, rule-based gate. It errs toward rejection: a false
reject just falls back to a safe hedged template, which is acceptable. The
real content of templates is simple and human-reviewable.

It does NOT import from app.llm (validator must stay independent of the
provider). Detected violations are returned for logging.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

VALIDATOR_VERSION = "output-validator-0.1.0"

# Case-insensitive patterns. Conservative and explainable. These are safety
# heuristics, not clinical definitions.
_DIAGNOSIS_PATTERNS = [
    r"\byou (?:have|are suffering from|suffer from)\b.*\b(depression|anxiety|bipolar|ptsd|ocd|schizophreni\w*|disorder)\b",  # noqa: E501
    r"\b(you are|you're)\b.*\b(depressed|bipolar|schizophrenic|psychotic)\b",
    r"\bthis is\b.*\b(depression|anxiety disorder|bipolar disorder|a disorder|a mental illness)\b",
    r"\byou (?:likely )?have a\b.*\bdisorder\b",
]
_MEDICATION_PATTERNS = [
    r"\b(take|start|try|use|prescrib\w*)\b.*\b(medication|medicine|antidepressant\w*|ssri\w*|xanax|prozac|zoloft|pills?|dose|dosage)\b",  # noqa: E501
    r"\byou should (?:see a psychiatrist to get|get)\b.*\b(medication|prescription)\b",
]
_CAUSE_PATTERNS = [
    r"\bthis is because of your\b",
    r"\bthe (?:real )?(?:reason|cause) is your\b",
    r"\byou feel this way because of (?:your )?(?:trauma|abuse|childhood|divorce|breakup)\b",
    r"\bit'?s (?:all )?because (?:of )?your\b",
]

_ALL = {
    "diagnosis": _DIAGNOSIS_PATTERNS,
    "medication": _MEDICATION_PATTERNS,
    "unstated_cause": _CAUSE_PATTERNS,
}
_COMPILED = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats] for cat, pats in _ALL.items()
}

# Safe, hedged fallback templates per language/script. Deliberately generic,
# question-form, and correctable. (Human review can refine wording later.)
_FALLBACK_TEMPLATES = {
    "en": "I might be misreading this. Can you tell me a little more about how you're feeling right now?",  # noqa: E501
    "roman_ur": "Shayad main theek se nahi samajh paya. Kya aap thora aur bata sakte hain ke is waqt aap kaisa mehsoos kar rahe hain?",  # noqa: E501
}


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating a reply."""

    ok: bool
    violations: list[str] = field(default_factory=list)
    validator_version: str = VALIDATOR_VERSION


def validate_reply(text: str) -> ValidationResult:
    """Return a ValidationResult; ok=False lists the violated categories."""
    violations: list[str] = []
    for category, patterns in _COMPILED.items():
        if any(p.search(text) for p in patterns):
            violations.append(category)
    return ValidationResult(ok=not violations, violations=violations)


def fallback_template(language: str) -> str:
    """Safe hedged fallback for the given language (defaults to English)."""
    return _FALLBACK_TEMPLATES.get(language, _FALLBACK_TEMPLATES["en"])


def validate_or_fallback(text: str, language: str = "en") -> tuple[str, ValidationResult]:
    """Return the reply if valid, otherwise a safe template.

    Always returns something safe to show the user, plus the result for logging.
    """
    result = validate_reply(text)
    if result.ok:
        return text, result
    return fallback_template(language), result
