"""Request/response models for the v1 API (Pydantic)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ---- Mood ----
class MoodCreate(BaseModel):
    mood: int = Field(ge=1, le=5, description="1 (very low) .. 5 (very good)")
    note: str | None = Field(default=None, max_length=1000)


class MoodEntry(BaseModel):
    id: str
    mood: int
    note: str | None = None
    created_at: datetime


class TrendPoint(BaseModel):
    day: str  # ISO date (YYYY-MM-DD)
    average_mood: float
    count: int


class MoodTrends(BaseModel):
    window_days: int
    points: list[TrendPoint]


# ---- Memory ----
class MemoryItem(BaseModel):
    id: str
    content: str
    created_at: datetime
    updated_at: datetime


class MemoryUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MemoryList(BaseModel):
    items: list[MemoryItem]


# ---- Consent ----
class ConsentCreate(BaseModel):
    consent_type: str = Field(min_length=1, max_length=100)


class ConsentRecord(BaseModel):
    id: str
    consent_type: str
    granted_at: datetime
    revoked_at: datetime | None = None

# ---- Chat ----
class HistoryTurn(BaseModel):
    """A past user message + its detected emotion (the user's own data)."""

    text: str = Field(min_length=1, max_length=4000)
    emotion: str | None = None
    language: str = "en"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[HistoryTurn] = Field(default_factory=list, max_length=200)
    # Insight keys the user said were wrong; they are never shown again.
    dismissed_insights: list[str] = Field(default_factory=list, max_length=100)


class InsightOut(BaseModel):
    """A hedged, correctable observation, with the user's own words as proof."""

    key: str
    question: str
    evidence: list[str]


class ChatResponse(BaseModel):
    reply: str
    language: str
    strategy: str
    emotion: str | None = None
    confidence: float
    is_crisis: bool
    used_fallback: bool
    nuances: list[str] = []
    insights: list[InsightOut] = []