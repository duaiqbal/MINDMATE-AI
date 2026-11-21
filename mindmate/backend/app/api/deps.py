"""FastAPI dependencies: current user + repository.

These are overridden in tests via app.dependency_overrides. In production the
repository will be a SupabaseRepository bound to the request's verified JWT so
that RLS applies; current_user will come from the validated token.
"""

from __future__ import annotations

from app.db.repository import InMemoryRepository, Repository

# A single in-memory repo instance as the default (dev/test). Production wiring
# replaces this via dependency override.
_default_repo = InMemoryRepository()


def get_repository() -> Repository:
    return _default_repo


def get_current_user_id() -> str:
    # Overridden in tests / replaced by JWT-derived id in production.
    raise RuntimeError(
        "get_current_user_id must be provided by auth wiring or a test override"
    )