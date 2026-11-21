"""Chat endpoint: runs the full orchestration pipeline.

The LLM gateway comes from ``get_gateway``. With an OpenRouter API key in the
environment it returns a real gateway; without one it returns None and the
pipeline answers with a safe template. Crisis resources come from the DB once
humans populate it.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse, InsightOut
from app.chat import respond
from app.config import LlmSettings
from app.llm.gateway import GatewayConfig, LlmGateway
from app.llm.openrouter import make_openrouter_provider
from app.longitudinal.patterns import Turn

router = APIRouter(prefix="/v1", tags=["chat"])


def get_gateway() -> LlmGateway | None:
    """Return the configured LLM gateway, or None (=> safe template fallback).

    Settings are read per request, so adding the key to backend/.env takes
    effect without restarting the server.
    """
    settings = LlmSettings()
    key = settings.api_key()
    if key is None:
        return None
    provider = make_openrouter_provider(
        api_key=key,
        base_url=settings.llm_base_url,
        timeout_seconds=settings.llm_timeout_seconds,
        fallback_models=settings.fallbacks(),
    )
    return LlmGateway(
        GatewayConfig(
            model_name=settings.llm_model_name,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        ),
        provider,
    )


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