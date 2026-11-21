"""Live verification of the init migration against an ephemeral Postgres.

Spins up pgserver (self-contained, no admin), installs a minimal Supabase
`auth` shim, applies the real migration, then checks:
  * RLS enabled (pg_class.relrowsecurity) on all 9 tables
  * ON DELETE CASCADE FKs to auth.users on all 8 user tables
  * a live cross-user isolation smoke test using auth.uid()

Run: python tools/verify_migration_live.py
Exits non-zero on any failure.
"""

import sys
import uuid
from pathlib import Path

import pgserver
import psycopg

BACKEND = Path(__file__).resolve().parents[1]
MIGRATION = (
    BACKEND.parent / "supabase" / "migrations" / "20250101000000_init_schema.sql"
)

USER_TABLES = [
    "profiles", "consents", "conversations", "messages", "analyses",
    "mood_logs", "memory_items", "audit_log",
]
ALL_TABLES = USER_TABLES + ["crisis_resources"]

# Minimal Supabase shim so the migration runs on bare Postgres exactly as it
# would on Supabase (auth.users table + auth.uid() reading a GUC claim).
AUTH_SHIM = """
create schema if not exists auth;
create table if not exists auth.users (
    id uuid primary key default gen_random_uuid()
);
create or replace function auth.uid() returns uuid
language sql stable as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
$$;
do $$ begin if not exists (select from pg_roles where rolname='authenticated') then create role authenticated; end if; end $$;
"""


def main() -> int:
    failures: list[str] = []
    import shutil
    data_dir = BACKEND / ".pg_verify"
    if data_dir.exists():
        shutil.rmtree(data_dir, ignore_errors=True)
    db = pgserver.get_server(str(data_dir))
    try:
        dsn = db.get_uri()
        with psycopg.connect(dsn, autocommit=True) as conn:
            cur = conn.cursor()
            cur.execute(AUTH_SHIM)
            cur.execute(MIGRATION.read_text(encoding="utf-8"))
            # Supabase grants these to the authenticated role by default; on bare
            # Postgres we grant them so RLS (not a missing GRANT) governs access.
            cur.execute(
                "grant usage on schema public to authenticated; "
                "grant select, insert, update, delete on all tables "
                "in schema public to authenticated;"
            )

            # 1) RLS enabled on every table
            cur.execute(
                "select relname, relrowsecurity from pg_class "
                "where relname = any(%s) and relnamespace = 'public'::regnamespace",
                (ALL_TABLES,),
            )
            rls = dict(cur.fetchall())
            for t in ALL_TABLES:
                if rls.get(t) is not True:
                    failures.append(f"RLS not enabled on {t} (got {rls.get(t)})")

            # 2) ON DELETE CASCADE FK to auth.users on user tables
            cur.execute(
                """
                select c.relname
                from pg_constraint con
                join pg_class c on c.oid = con.conrelid
                join pg_class f on f.oid = con.confrelid
                join pg_namespace fn on fn.oid = f.relnamespace
                where con.contype = 'f'
                  and f.relname = 'users' and fn.nspname = 'auth'
                  and con.confdeltype = 'c'
                """
            )
            cascading = {r[0] for r in cur.fetchall()}
            for t in USER_TABLES:
                if t not in cascading:
                    failures.append(f"{t} missing ON DELETE CASCADE to auth.users")

            # 3) Live cross-user isolation smoke test on mood_logs
            u1, u2 = uuid.uuid4(), uuid.uuid4()
            cur.execute("insert into auth.users(id) values (%s),(%s)", (u1, u2))
            # Insert one mood row per user, as that user, under RLS.
            with psycopg.connect(dsn) as c1:
                cc = c1.cursor()
                cc.execute("set role authenticated")
                cc.execute("select set_config('request.jwt.claim.sub', %s, false)", (str(u1),))
                cc.execute("insert into public.mood_logs(user_id, mood) values (%s, 3)", (u1,))
                c1.commit()
                # u1 sees exactly 1 row
                cc.execute("select count(*) from public.mood_logs")
                n1 = cc.fetchone()[0]
                if n1 != 1:
                    failures.append(f"user1 should see 1 mood row, saw {n1}")
            with psycopg.connect(dsn) as c2:
                cc = c2.cursor()
                cc.execute("set role authenticated")
                cc.execute("select set_config('request.jwt.claim.sub', %s, false)", (str(u2),))
                # u2 must see 0 of u1's rows
                cc.execute("select count(*) from public.mood_logs")
                n2 = cc.fetchone()[0]
                if n2 != 0:
                    failures.append(f"user2 must NOT see user1 rows, saw {n2}")
                # u2 cannot insert a row owned by u1
                try:
                    cc.execute("insert into public.mood_logs(user_id, mood) values (%s, 2)", (u1,))
                    c2.commit()
                    failures.append("user2 was able to insert a row owned by user1")
                except psycopg.errors.Error:
                    c2.rollback()  # expected: RLS with_check denies it

            # 4) cascade actually deletes dependent rows
            with psycopg.connect(dsn, autocommit=True) as cadm:
                ca = cadm.cursor()
                ca.execute("delete from auth.users where id = %s", (u1,))
                ca.execute("select count(*) from public.mood_logs where user_id = %s", (u1,))
                left = ca.fetchone()[0]
                if left != 0:
                    failures.append(f"cascade failed: {left} mood rows remain for deleted user")
    finally:
        db.cleanup()

    if failures:
        print("LIVE VERIFICATION FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("LIVE VERIFICATION PASSED: RLS + cascade + cross-user isolation OK")
    print(f"  tables checked: {', '.join(ALL_TABLES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())