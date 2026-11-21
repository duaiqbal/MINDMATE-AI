"""Health check endpoint.

Deliberately requires NO secrets so the service can report liveness even
before Supabase/LLM config is supplied.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return a simple liveness payload."""
    return {"status": "ok"}
