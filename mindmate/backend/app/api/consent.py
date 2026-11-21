"""Consent endpoints: grant + list consents."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id, get_repository
from app.api.schemas import ConsentCreate, ConsentRecord
from app.db.repository import Repository

router = APIRouter(prefix="/v1", tags=["consent"])


@router.post("/consent", response_model=ConsentRecord, status_code=201)
def grant_consent(
    body: ConsentCreate,
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> ConsentRecord:
    return ConsentRecord(**repo.add_consent(user_id, body.consent_type))


@router.get("/consent", response_model=list[ConsentRecord])
def list_consents(
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> list[ConsentRecord]:
    return [ConsentRecord(**r) for r in repo.list_consents(user_id)]