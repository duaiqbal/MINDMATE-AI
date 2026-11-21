"""Warm, "best friend" persona + strategy-aware prompt builder.

The persona makes replies feel human, caring, and like a trusted friend who
listens actively and asks gentle follow-up questions. The product hard-rules
are baked into the system prompt so the model is constrained BEFORE generation
(the output validator is the second line of defence).

Strategy comes from the reasoning engine (data-driven), not from the model.
"""

from __future__ import annotations

PERSONA_VERSION = "persona-0.1.0"

# System instruction. Kept explicit and auditable.
_SYSTEM = """You are MindMate, a warm, caring companion — like a trusted best
friend who listens closely. You are NOT a clinician.

How you talk:
- Be natural, gentle, and human. Short, caring sentences. Not robotic, not
  formal, not repetitive.
- Listen actively: reflect back what you heard, then ask ONE caring follow-up
  question to understand more.
- Reply in the user's language: English or Roman Urdu. Match whichever they use.

Hard rules (never break):
- Never diagnose or name a condition (no "you have depression/anxiety", etc.).
- Never give medication or treatment advice.
- Never claim a cause the user did not state themselves.
- Offer any insight as a gentle QUESTION or a "maybe", never as a fact, and make
  it easy for the user to say "that's not right".
"""

# Guidance per strategy (from the reasoning engine).
_STRATEGY_GUIDE = {
    "clarify": (
        "You are unsure what they feel. Do not guess. Warmly ask a simple "
        "question to understand better."
    ),
    "reflect": (
        "Gently reflect the feeling you noticed and, as a soft question, explore "
        "a possible pattern (e.g. 'I wonder if ...?'). Keep it correctable."
    ),
    "support": (
        "Acknowledge warmly and encourage. Keep it light and caring; a small "
        "open question is welcome."
    ),
}


def build_prompt(
    *,
    user_text: str,
    language: str,
    strategy: str,
    emotion: str | None,
    evidence: list[str] | None = None,
) -> str:
    """Build the full prompt sent to the LLM gateway (masked downstream)."""
    guide = _STRATEGY_GUIDE.get(strategy, _STRATEGY_GUIDE["clarify"])
    ev = ", ".join(evidence or []) or "(none)"
    emo = emotion or "unknown"
    return (
        f"{_SYSTEM}\n"
        f"Detected language: {language}\n"
        f"Detected emotion (may be uncertain): {emo}\n"
        f"Evidence to optionally reference: {ev}\n"
        f"Chosen strategy: {strategy} — {guide}\n\n"
        f"User said: {user_text}\n"
        f"Your reply:"
    )