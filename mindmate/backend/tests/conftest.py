"""Shared pytest fixtures.

Provides an ephemeral Postgres (via pgserver) with the Supabase `auth` shim and
the real migration applied, so RLS behaviour can be tested without a live
Supabase project. If pgserver is not installed, DB-backed tests are skipped.
"""

import shutil
import uuid
from pathlib import Path

import pytest

try:
    import pgserver  # type: ignore
    import psycopg  # type: ignore

    HAS_PG = True
except Exception:  # pragma: no cover - environment-dependent
    HAS_PG = False

BACKEND = Path(__file__).resolve().parent.parent
MIGRATION = (
    BACKEND.parent / "supabase" / "migrations" / "20250101000000_init_schema.sql"
)

AUTH_SHIM = """
create schema if not exists auth;
create table if not exists auth.users (
    id uuid primary key default gen_random_uuid()
);
create or replace function auth.uid() returns uuid
language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;
do $$ begin
  if not exists (select from pg_roles where rolname='authenticated') then
    create role authenticated;
  end if;
end $$;
"""

GRANTS = (
    "grant usage on schema public to authenticated; "
    "grant select, insert, update, delete on all tables "
    "in schema public to authenticated;"
)


@pytest.fixture(scope="session")
def pg_dsn():
    """Start an ephemeral Postgres, apply shim + migration, yield its DSN."""
    if not HAS_PG:
        pytest.skip("pgserver/psycopg not installed; DB-backed tests skipped")

    data_dir = BACKEND / ".pg_test"
    if data_dir.exists():
        shutil.rmtree(data_dir, ignore_errors=True)
    db = pgserver.get_server(str(data_dir))
    try:
        dsn = db.get_uri()
        with psycopg.connect(dsn, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(AUTH_SHIM)
            cur.execute(MIGRATION.read_text(encoding="utf-8"))
            cur.execute(GRANTS)
        yield dsn
    finally:
        db.cleanup()
        shutil.rmtree(data_dir, ignore_errors=True)


@pytest.fixture
def make_user(pg_dsn):
    """Factory: create an auth user and return its uuid."""
    import psycopg

    created: list[uuid.UUID] = []

    def _make() -> uuid.UUID:
        uid = uuid.uuid4()
        with psycopg.connect(pg_dsn, autocommit=True) as conn:
            conn.cursor().execute("insert into auth.users(id) values (%s)", (uid,))
        created.append(uid)
        return uid

    return _make

@pytest.fixture(autouse=True)
def _no_real_llm(monkeypatch):
    """Never call the real LLM from tests, even if backend/.env has a key.

    An empty env var overrides the .env file; LlmSettings treats it as unset.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
