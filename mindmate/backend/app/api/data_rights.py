"""Data-rights endpoints: export all data, delete account + all data."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id, get_repository
from app.db.repository import Repository

router = APIRouter(prefix="/v1", tags=["data-rights"])


@router.get("/export")
def export_data(
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> dict:
    """Return all of the user's data as a portable JSON object."""
    return repo.export_all(user_id)


@router.delete("/account", status_code=204)
def delete_account(
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> None:
    """Delete the user's data. In production this also cascades from auth.users."""
    repo.delete_all(user_id)