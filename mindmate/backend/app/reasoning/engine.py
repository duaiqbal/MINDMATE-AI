"""Reasoning engine: pick a response strategy from an auditable rule table.

Strategy logic is DATA (config/reasoning_rules.yaml), not scattered ifs. The
engine evaluates rules in order and returns the first match. The uncertainty
gate is just one rule: confidence below the clarify threshold -> "clarify".

Everything is deterministic and logs the rule-table + threshold versions for
reproducibility (see tech.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

VALID_EMOTIONS = {"joy", "sadness", "fear_anxiety", "anger", "neutral"}
VALID_STRATEGIES = {"crisis_response", "clarify", "reflect", "support"}

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


@dataclass(frozen=True)
class ReasoningInput:
    """Inputs to a reasoning decision."""

    emotion: str
    confidence: float
    crisis: bool = False

    def __post_init__(self) -> None:
        if self.emotion not in VALID_EMOTIONS:
            raise ValueError(f"unknown emotion: {self.emotion!r}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence out of range: {self.confidence}")


@dataclass(frozen=True)
class Decision:
    """Result of a reasoning decision, with provenance for logging."""

    strategy: str
    matched_rule: str
    rule_table_version: str
    threshold_version: str
    thresholds_used: dict[str, float] = field(default_factory=dict)


class ReasoningEngine:
    """Evaluates the YAML decision table against a ReasoningInput."""

    def __init__(self, rules_doc: dict[str, Any], thresholds_doc: dict[str, Any]):
        self._rule_table_version = rules_doc.get("version", "unknown")
        self._threshold_version = thresholds_doc.get("version", "unknown")
        self._rules = rules_doc.get("rules", [])
        self._default = rules_doc.get("default_strategy", "clarify")
        # thresholds: everything except the version key
        self._thresholds = {
            k: float(v)
            for k, v in thresholds_doc.items()
            if k != "version"
        }
        self._validate()

    def _validate(self) -> None:
        for rule in self._rules:
            strat = rule.get("strategy")
            if strat not in VALID_STRATEGIES:
                raise ValueError(f"rule {rule.get('name')!r} has invalid strategy {strat!r}")
        if self._default not in VALID_STRATEGIES:
            raise ValueError(f"invalid default_strategy {self._default!r}")

    def _resolve_threshold(self, ref: Any) -> float:
        """Resolve 'threshold.<name>' references to a numeric threshold."""
        if isinstance(ref, int | float):
            return float(ref)
        if isinstance(ref, str) and ref.startswith("threshold."):
            name = ref.split(".", 1)[1]
            if name not in self._thresholds:
                raise KeyError(f"threshold {name!r} not defined")
            return self._thresholds[name]
        raise ValueError(f"cannot resolve threshold reference: {ref!r}")

    def _matches(self, when: dict[str, Any], inp: ReasoningInput) -> bool:
        for key, expected in when.items():
            if key == "crisis":
                if bool(inp.crisis) is not bool(expected):
                    return False
            elif key == "confidence_below":
                if not (inp.confidence < self._resolve_threshold(expected)):
                    return False
            elif key == "emotion_in":
                if inp.emotion not in set(expected):
                    return False
            else:
                raise ValueError(f"unknown rule condition: {key!r}")
        return True

    def decide(self, inp: ReasoningInput) -> Decision:
        for rule in self._rules:
            when = rule.get("when", {})
            if self._matches(when, inp):
                return Decision(
                    strategy=rule["strategy"],
                    matched_rule=rule.get("name", "unnamed"),
                    rule_table_version=self._rule_table_version,
                    threshold_version=self._threshold_version,
                    thresholds_used=dict(self._thresholds),
                )
        return Decision(
            strategy=self._default,
            matched_rule="__default__",
            rule_table_version=self._rule_table_version,
            threshold_version=self._threshold_version,
            thresholds_used=dict(self._thresholds),
        )


def load_engine(
    rules_path: Path | None = None,
    thresholds_path: Path | None = None,
) -> ReasoningEngine:
    """Load the engine from YAML config (defaults to backend/config)."""
    rules_path = rules_path or (_CONFIG_DIR / "reasoning_rules.yaml")
    thresholds_path = thresholds_path or (_CONFIG_DIR / "thresholds.yaml")
    rules_doc = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    thresholds_doc = yaml.safe_load(thresholds_path.read_text(encoding="utf-8"))
    return ReasoningEngine(rules_doc, thresholds_doc)