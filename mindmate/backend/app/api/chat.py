"""Chat endpoint: runs the full orchestration pipeline.

The LLM gateway is injected via a dependency so it can be wired to a real
provider later (Groq/Qwen/Llama per the proposal) or left None (safe template
fallback). Crisis resources come from the DB once humans populate it.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse, InsightOut
from app.chat import respond
from app.llm.gateway import LlmGateway
from app.longitudinal.patterns import Turn

router = APIRouter(prefix="/v1", tags=["chat"])


def get_gateway() -> LlmGateway | None:
    """Return the configured LLM gateway, or None (=> safe template fallback)."""
    return None


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    gateway: LlmGateway | None = Depends(get_gateway),
) -> ChatResponse:
    history = [Turn(t.text, t.emotion, t.language) for t in body.history]
    result = respond(
        body.message,
        gateway=gateway,
        history=history,
        dismissed_insights=set(body.dismissed_insights),
    )
    return ChatResponse(
        reply=result.reply,
        language=result.language,
        strategy=result.strategy,
        emotion=result.emotion,
        confidence=result.confidence,
        is_crisis=result.is_crisis,
        used_fallback=result.used_fallback,
        nuances=result.nuances,
        insights=[
            InsightOut(key=i.key, question=i.question, evidence=i.evidence)
            for i in result.insights
        ],
    )