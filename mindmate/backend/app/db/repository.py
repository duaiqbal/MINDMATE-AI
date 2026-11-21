"""Data-access protocol + an in-memory implementation for tests.

The API layer depends on this protocol, not on Supabase directly. The real
SupabaseRepository (added when live keys exist) will verify the user JWT and
query with the user's token so RLS applies. The in-memory repo lets us test
business logic and endpoint behaviour deterministically.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import Protocol


def _now() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return str(uuid.uuid4())


class Repository(Protocol):
    """Per-user data access. Every method is scoped to ``user_id``."""

    def add_mood(self, user_id: str, mood: int, note: str | None) -> dict: ...
    def list_moods(self, user_id: str, since: datetime) -> list[dict]: ...
    def list_memory(self, user_id: str) -> list[dict]: ...
    def update_memory(self, user_id: str, item_id: str, content: str) -> dict | None: ...
    def delete_memory(self, user_id: str, item_id: str) -> bool: ...
    def add_memory(self, user_id: str, content: str) -> dict: ...
    def add_consent(self, user_id: str, consent_type: str) -> dict: ...
    def list_consents(self, user_id: str) -> list[dict]: ...
    def export_all(self, user_id: str) -> dict: ...
    def delete_all(self, user_id: str) -> int: ...


class InMemoryRepository:
    """Dict-backed repo that mimics per-user isolation (like RLS would)."""

    def __init__(self) -> None:
        self._moods: dict[str, list[dict]] = defaultdict(list)
        self._memory: dict[str, list[dict]] = defaultdict(list)
        self._consents: dict[str, list[dict]] = defaultdict(list)

    def add_mood(self, user_id: str, mood: int, note: str | None) -> dict:
        row = {"id": _new_id(), "mood": mood, "note": note, "created_at": _now()}
        self._moods[user_id].append(row)
        return row

    def list_moods(self, user_id: str, since: datetime) -> list[dict]:
        return [m for m in self._moods[user_id] if m["created_at"] >= since]

    def add_memory(self, user_id: str, content: str) -> dict:
        now = _now()
        row = {"id": _new_id(), "content": content, "created_at": now, "updated_at": now}
        self._memory[user_id].append(row)
        return row

    def list_memory(self, user_id: str) -> list[dict]:
        return list(self._memory[user_id])

    def update_memory(self, user_id: str, item_id: str, content: str) -> dict | None:
        for row in self._memory[user_id]:
            if row["id"] == item_id:
                row["content"] = content
                row["updated_at"] = _now()
                return row
        return None

    def delete_memory(self, user_id: str, item_id: str) -> bool:
        items = self._memory[user_id]
        for i, row in enumerate(items):
            if row["id"] == item_id:
                del items[i]
                return True
        return False

    def add_consent(self, user_id: str, consent_type: str) -> dict:
        row = {
            "id": _new_id(),
            "consent_type": consent_type,
            "granted_at": _now(),
            "revoked_at": None,
        }
        self._consents[user_id].append(row)
        return row

    def list_consents(self, user_id: str) -> list[dict]:
        return list(self._consents[user_id])

    def export_all(self, user_id: str) -> dict:
        """Return all of a user's data as a portable dict (data-rights)."""
        return {
            "user_id": user_id,
            "moods": list(self._moods[user_id]),
            "memory": list(self._memory[user_id]),
            "consents": list(self._consents[user_id]),
        }

    def delete_all(self, user_id: str) -> int:
        """Delete all of a user's data; return the number of rows removed."""
        count = (
            len(self._moods[user_id])
            + len(self._memory[user_id])
            + len(self._consents[user_id])
        )
        self._moods.pop(user_id, None)
        self._memory.pop(user_id, None)
        self._consents.pop(user_id, None)
        return count