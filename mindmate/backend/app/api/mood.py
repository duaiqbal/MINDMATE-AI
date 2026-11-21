"""Mood endpoints: log a mood, read a simple trend."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id, get_repository
from app.api.schemas import MoodCreate, MoodEntry, MoodTrends
from app.db.repository import Repository
from app.longitudinal import compute_trend

router = APIRouter(prefix="/v1", tags=["mood"])


@router.post("/mood", response_model=MoodEntry, status_code=201)
def create_mood(
    body: MoodCreate,
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> MoodEntry:
    row = repo.add_mood(user_id, body.mood, body.note)
    return MoodEntry(**row)


@router.get("/mood/trends", response_model=MoodTrends)
def mood_trends(
    window_days: int = Query(default=7, ge=1, le=90),
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> MoodTrends:
    since = datetime.now(UTC) - timedelta(days=window_days)
    moods = repo.list_moods(user_id, since)
    points = compute_trend(moods, window_days)
    return MoodTrends(window_days=window_days, points=points)