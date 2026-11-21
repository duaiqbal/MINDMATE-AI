"""Chat orchestration: wires normalize -> lang -> safety -> emotion ->
reasoning -> prompt -> gateway -> validator into one pipeline."""

from app.chat.orchestrator import ChatResult, respond
from app.chat.persona import PERSONA_VERSION, build_prompt

__all__ = ["respond", "ChatResult", "build_prompt", "PERSONA_VERSION"]