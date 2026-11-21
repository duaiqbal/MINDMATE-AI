"""End-to-end chat pipeline.

Order (safety first, LLM last, validator as a guard):
  normalize -> language id -> SAFETY (crisis => fixed response, no LLM)
  -> emotion (uncertain/missing => low confidence) -> nuance tagging
  -> history patterns (hedged questions) -> reasoning gate (YAML)
  -> prompt -> LLM gateway -> output validator.

Everything degrades safely:
  * emotion model missing  -> confidence 0.0 -> gate picks "clarify"
  * LLM provider missing/fails -> safe template fallback
  * reply violates hard-rules -> replaced by safe template

A provenance dict (versions) is returned for reproducible logging.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.chat.persona import PERSONA_VERSION, build_prompt
from app.emotion.classifier import EmotionClassifier, ModelNotAvailable
from app.emotion.nuance import tag_nuances
from app.language.identifier import identify
from app.language.normalizer import NORMALIZER_VERSION, normalize
from app.llm.gateway import LlmError, LlmGateway
from app.longitudinal.patterns import PATTERNS_VERSION, Insight, Turn, detect_patterns
from app.reasoning import ReasoningInput, load_engine
from app.safety.detector import build_fixed_response, check_crisis
from app.safety.models import CrisisResource
from app.validator import validate_or_fallback

# Only offer a pattern when we are reasonably sure about the strategy: a
# "clarify" turn (unsure what the user feels) should ask, not interpret.
_INSIGHT_STRATEGIES = {"reflect", "support"}


@dataclass(frozen=True)
class ChatResult:
    reply: str
    language: str
    strategy: str
    emotion: str | None
    confidence: float
    is_crisis: bool
    used_fallback: bool
    nuances: list[str] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)


def respond(
    user_text: str,
    *,
    gateway: LlmGateway | None = None,
    classifier: EmotionClassifier | None = None,
    crisis_resources: list[CrisisResource] | None = None,
    history: list[Turn] | None = None,
    dismissed_insights: set[str] | frozenset[str] = frozenset(),
) -> ChatResult:
    """Run one user message through the full pipeline and return a reply."""
    normalized = normalize(user_text)
    lang = identify(user_text)

    provenance = {
        "normalizer_version": NORMALIZER_VERSION,
        "lang_id_version": lang.version,
        "persona_version": PERSONA_VERSION,
    }

    # 1) SAFETY FIRST. On crisis, return a fixed response. The LLM is NOT called.
    crisis = check_crisis(normalized)
    provenance["lexicon_version"] = crisis.lexicon_version
    if crisis.is_crisis:
        reply = build_fixed_response(crisis_resources or [], lang.language)
        return ChatResult(
            reply=reply,
            language=lang.language,
            strategy="crisis_response",
            emotion=None,
            confidence=1.0,
            is_crisis=True,
            used_fallback=False,
            provenance=provenance,
        )

    # 2) Emotion (uncertain or missing model -> low confidence).
    emotion: str | None = None
    confidence = 0.0
    classifier = classifier or EmotionClassifier()
    try:
        pred = classifier.predict(normalized)
        emotion, confidence = pred.label, pred.confidence
        provenance["model_version"] = pred.model_version
    except ModelNotAvailable:
        provenance["model_version"] = "model-missing"

    # 2b) Self-discovery nuances (rule-based; gentle possibilities only).
    nuances: list[str] = []
    if emotion is not None:
        nres = tag_nuances(emotion, normalized, lang.language)
        nuances = nres.nuances
        provenance["taxonomy_version"] = nres.taxonomy_version

    # 3) Reasoning gate (data-driven strategy). Low confidence -> clarify.
    engine = load_engine()
    decision = engine.decide(
        ReasoningInput(emotion=emotion or "neutral", confidence=confidence)
    )
    provenance["rule_table_version"] = decision.rule_table_version
    provenance["threshold_version"] = decision.threshold_version

    # 3b) Patterns across the conversation (hedged questions, with evidence).
    insights: list[Insight] = []
    if history and decision.strategy in _INSIGHT_STRATEGIES:
        turns = [*history, Turn(user_text, emotion, lang.language)]
        insights = detect_patterns(
            turns, language=lang.language, dismissed=dismissed_insights
        )
        provenance["patterns_version"] = PATTERNS_VERSION

    # 4) Build prompt + call the LLM. No gateway/provider -> safe template.
    evidence = [*nuances]
    evidence += [f"possible pattern, ask gently: {i.question}" for i in insights]
    prompt = build_prompt(
        user_text=user_text,
        language=lang.language,
        strategy=decision.strategy,
        emotion=emotion,
        evidence=evidence,
    )

    used_fallback = False
    if gateway is None:
        raw_reply = ""
        used_fallback = True
    else:
        provenance["llm_model"] = gateway.model_name
        try:
            raw_reply = gateway.complete(prompt)
            provenance["llm_model_used"] = gateway.last_model_used
        except LlmError:
            raw_reply = ""
            used_fallback = True

    # 5) Validate the reply (hard-rules). Violations -> safe template.
    if raw_reply:
        reply, result = validate_or_fallback(raw_reply, lang.language)
        if not result.ok:
            used_fallback = True
        provenance["validator_version"] = result.validator_version
    else:
        from app.validator.output_validator import (
            VALIDATOR_VERSION,
            fallback_template,
        )

        reply = fallback_template(lang.language)
        provenance["validator_version"] = VALIDATOR_VERSION
        used_fallback = True

    return ChatResult(
        reply=reply,
        language=lang.language,
        strategy=decision.strategy,
        emotion=emotion,
        confidence=confidence,
        is_crisis=False,
        used_fallback=used_fallback,
        nuances=nuances,
        insights=insights,
        provenance=provenance,
    )