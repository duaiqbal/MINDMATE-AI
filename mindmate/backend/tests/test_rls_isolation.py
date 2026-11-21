"""Cross-user isolation test plan (RLS).

Verifies, against a real Postgres with the migration applied, that a user can
only see and modify their own rows. Runs via the ephemeral pgserver fixture;
skipped automatically if pgserver is unavailable.

On a real Supabase test project the same assertions hold; the auth.uid() shim
here mirrors Supabase's JWT 'sub' claim.
"""

import pytest

psycopg = pytest.importorskip(
    "psycopg",
    reason="psycopg/libpq not loadable in this environment; RLS tests skipped",
)


def _as_user(dsn: str, uid):
    """Return a connection acting as the given authenticated user."""
    conn = psycopg.connect(dsn)
    cur = conn.cursor()
    cur.execute("set role authenticated")
    cur.execute("select set_config('request.jwt.claim.sub', %s, false)", (str(uid),))
    return conn, cur


def test_user_sees_only_own_mood_rows(pg_dsn, make_user):
    u1 = make_user()
    u2 = make_user()

    conn1, cur1 = _as_user(pg_dsn, u1)
    cur1.execute("insert into public.mood_logs(user_id, mood) values (%s, 3)", (u1,))
    conn1.commit()
    cur1.execute("select count(*) from public.mood_logs")
    assert cur1.fetchone()[0] == 1
    conn1.close()

    conn2, cur2 = _as_user(pg_dsn, u2)
    cur2.execute("select count(*) from public.mood_logs")
    assert cur2.fetchone()[0] == 0, "user2 must not see user1's rows"
    conn2.close()


def test_user_cannot_insert_row_owned_by_another(pg_dsn, make_user):
    owner = make_user()
    attacker = make_user()

    conn, cur = _as_user(pg_dsn, attacker)
    with pytest.raises(psycopg.errors.Error):
        cur.execute(
            "insert into public.mood_logs(user_id, mood) values (%s, 2)", (owner,)
        )
        conn.commit()
    conn.rollback()
    conn.close()


def test_user_cannot_update_another_users_row(pg_dsn, make_user):
    owner = make_user()
    attacker = make_user()

    conn_o, cur_o = _as_user(pg_dsn, owner)
    cur_o.execute(
        "insert into public.memory_items(user_id, content) values (%s, 'mine') "
        "returning id",
        (owner,),
    )
    item_id = cur_o.fetchone()[0]
    conn_o.commit()
    conn_o.close()

    conn_a, cur_a = _as_user(pg_dsn, attacker)
    # RLS makes the other user's row invisible, so the update affects 0 rows.
    cur_a.execute(
        "update public.memory_items set content = 'hacked' where id = %s", (item_id,)
    )
    assert cur_a.rowcount == 0, "attacker must not update another user's row"
    conn_a.commit()
    conn_a.close()

    # Confirm the owner's content is unchanged.
    conn_o2, cur_o2 = _as_user(pg_dsn, owner)
    cur_o2.execute("select content from public.memory_items where id = %s", (item_id,))
    assert cur_o2.fetchone()[0] == "mine"
    conn_o2.close()


def test_delete_cascades_from_auth_users(pg_dsn, make_user):
    u = make_user()
    conn, cur = _as_user(pg_dsn, u)
    cur.execute("insert into public.mood_logs(user_id, mood) values (%s, 4)", (u,))
    conn.commit()
    conn.close()

    # Delete the auth user (admin/autocommit); dependent rows must be gone.
    with psycopg.connect(pg_dsn, autocommit=True) as admin:
        admin.cursor().execute("delete from auth.users where id = %s", (u,))

    with psycopg.connect(pg_dsn, autocommit=True) as check:
        c = check.cursor()
        c.execute("select count(*) from public.mood_logs where user_id = %s", (u,))
        assert c.fetchone()[0] == 0, "cascade delete should remove dependent rows"