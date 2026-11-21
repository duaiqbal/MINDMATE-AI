"""Static validation of the initial Supabase migration.

This does NOT run Postgres (no CLI/Docker in this environment). It checks:
  1. The whole file parses as valid Postgres SQL (sqlglot).
  2. Every expected table is created.
  3. Every user-owned table enables RLS.
  4. Every user-owned table cascades from auth.users (ON DELETE CASCADE).
  5. crisis_resources has NO foreign key to auth.users (no user PII owner).
  6. No hard-coded phone numbers were invented in the migration.

The authoritative acceptance gate remains `supabase db reset`, to be run when
the Supabase CLI/Docker are available.
"""

import re
from pathlib import Path

import sqlglot

MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "supabase"
    / "migrations"
    / "20250101000000_init_schema.sql"
)

USER_TABLES = [
    "profiles",
    "consents",
    "conversations",
    "messages",
    "analyses",
    "mood_logs",
    "memory_items",
    "audit_log",
]
ALL_TABLES = USER_TABLES + ["crisis_resources"]


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_file_exists() -> None:
    assert MIGRATION.is_file(), f"missing migration: {MIGRATION}"


def test_migration_parses_as_postgres() -> None:
    statements = sqlglot.parse(_sql(), read="postgres")
    assert statements, "no statements parsed"
    # None of the parsed top-level statements should be unparsable.
    assert all(s is not None for s in statements)


def test_all_tables_created() -> None:
    sql = _sql().lower()
    for table in ALL_TABLES:
        assert f"create table public.{table}" in sql, f"missing table {table}"


def test_rls_enabled_on_every_table() -> None:
    sql = _sql().lower()
    for table in ALL_TABLES:
        pattern = rf"alter table public\.{table}\s+enable row level security"
        assert re.search(pattern, sql), f"RLS not enabled on {table}"


def test_user_tables_cascade_from_auth_users() -> None:
    """Each user table must reference auth.users with ON DELETE CASCADE."""
    sql = _sql()
    for table in USER_TABLES:
        # Grab the CREATE TABLE block for this table.
        block = re.search(
            rf"create table public\.{table} \((.*?)\n\);",
            sql,
            re.DOTALL | re.IGNORECASE,
        )
        assert block, f"could not locate create block for {table}"
        body = block.group(1)
        assert re.search(
            r"references auth\.users \(id\) on delete cascade",
            body,
            re.IGNORECASE,
        ), f"{table} does not cascade from auth.users"


def test_crisis_resources_has_no_auth_users_fk() -> None:
    sql = _sql()
    block = re.search(
        r"create table public\.crisis_resources \((.*?)\n\);",
        sql,
        re.DOTALL | re.IGNORECASE,
    )
    assert block, "could not locate crisis_resources block"
    assert "auth.users" not in block.group(1).lower(), (
        "crisis_resources must not own user data / reference auth.users"
    )


def test_no_invented_phone_numbers() -> None:
    """No helpline phone numbers are hard-coded in the migration."""
    sql = _sql()
    # Any run of 5+ digits (optionally with separators) would be suspicious as a
    # phone number. Allow the single timestamp in the filename-style comment and
    # the mood/locale checks by scanning only string literals.
    literals = re.findall(r"'([^']*)'", sql)
    for lit in literals:
        digits = re.sub(r"\D", "", lit)
        assert len(digits) < 5, f"possible hard-coded number in literal: {lit!r}"