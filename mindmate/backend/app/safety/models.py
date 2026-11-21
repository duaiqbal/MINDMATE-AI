"""Schemas for the safety layer. Content is human-authored, not generated here."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrisisLexiconEntry:
    """One human-authored crisis lexicon entry.

    IMPORTANT: this project NEVER generates crisis phrases in code. Entries are
    authored and reviewed by people and loaded from a data file. This class is
    only the schema + validation.
    """

    phrase: str
    language: str  # en | ur | roman_ur
    severity: str  # e.g. "high" (human-defined taxonomy)

    def __post_init__(self) -> None:
        if not self.phrase.strip():
            raise ValueError("crisis lexicon entry phrase must be non-empty")
        if self.language not in {"en", "roman_ur"}:
            raise ValueError(f"unsupported language: {self.language!r}")


@dataclass(frozen=True)
class CrisisResource:
    """A helpline resource row (from the crisis_resources table).

    Phone numbers / URLs / names are NEVER hard-coded or invented in code,
    tests, or docs. They come from the database, populated by humans.
    """

    name: str
    phone: str | None = None
    url: str | None = None
    country_code: str | None = None
    language: str | None = None


@dataclass(frozen=True)
class CrisisCheck:
    """Result of a crisis check."""

    is_crisis: bool
    matched: list[str] = field(default_factory=list)
    lexicon_version: str = "unset"