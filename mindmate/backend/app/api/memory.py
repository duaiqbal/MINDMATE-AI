"""Memory endpoints: list, add, update, delete user-visible memory."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user_id, get_repository
from app.api.schemas import MemoryItem, MemoryList, MemoryUpdate
from app.db.repository import Repository

router = APIRouter(prefix="/v1", tags=["memory"])


@router.get("/memory", response_model=MemoryList)
def list_memory(
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> MemoryList:
    return MemoryList(items=[MemoryItem(**r) for r in repo.list_memory(user_id)])


@router.post("/memory", response_model=MemoryItem, status_code=201)
def add_memory(
    body: MemoryUpdate,
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> MemoryItem:
    return MemoryItem(**repo.add_memory(user_id, body.content))


@router.patch("/memory/{item_id}", response_model=MemoryItem)
def update_memory(
    item_id: str,
    body: MemoryUpdate,
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> MemoryItem:
    row = repo.update_memory(user_id, item_id, body.content)
    if row is None:
        raise HTTPException(status_code=404, detail="memory item not found")
    return MemoryItem(**row)


@router.delete("/memory/{item_id}", status_code=204)
def delete_memory(
    item_id: str,
    user_id: str = Depends(get_current_user_id),
    repo: Repository = Depends(get_repository),
) -> None:
    if not repo.delete_memory(user_id, item_id):
        raise HTTPException(status_code=404, detail="memory item not found")