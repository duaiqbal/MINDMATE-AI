-- MindMate AI — initial schema
-- Phase 0, Task 3: tables + Row Level Security + ON DELETE CASCADE.
--
-- Rules (see .kiro/steering/product.md and tech.md):
--   * RLS is ENABLED on every user-owned table; users access only their own rows.
--   * Every user table cascades from auth.users so deleting an auth user
--     removes their data.
--   * crisis_resources holds NO user PII and starts EMPTY (humans populate it);
--     no phone numbers are invented here.
--   * audit_log: clients may read their own rows; writes happen server-side via
--     the service role (which bypasses RLS). Final policy set in the safety phase.
--
-- Column sets are intentionally minimal; later phases add columns via new
-- migrations.

begin;

-- ---------------------------------------------------------------------------
-- profiles: one row per auth user (id == auth.users.id)
-- ---------------------------------------------------------------------------
create table public.profiles (
    id          uuid primary key references auth.users (id) on delete cascade,
    display_name text,
    locale      text not null default 'en'
                 check (locale in ('en', 'ur', 'roman_ur')),
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- consents: explicit, revocable consent records
-- ---------------------------------------------------------------------------
create table public.consents (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid not null references auth.users (id) on delete cascade,
    consent_type text not null,
    granted_at   timestamptz not null default now(),
    revoked_at   timestamptz
);

-- ---------------------------------------------------------------------------
-- conversations
-- ---------------------------------------------------------------------------
create table public.conversations (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references auth.users (id) on delete cascade,
    title      text,
    created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- messages: belong to a conversation and a user
-- ---------------------------------------------------------------------------
create table public.messages (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users (id) on delete cascade,
    conversation_id uuid not null
                     references public.conversations (id) on delete cascade,
    role            text not null check (role in ('user', 'assistant', 'system')),
    content         text not null,
    language        text check (language in ('en', 'ur', 'roman_ur')),
    created_at      timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- analyses: classifier output + reproducibility versions
-- ---------------------------------------------------------------------------
create table public.analyses (
    id               uuid primary key default gen_random_uuid(),
    user_id          uuid not null references auth.users (id) on delete cascade,
    message_id       uuid references public.messages (id) on delete cascade,
    emotion_label    text,
    confidence       double precision,
    strategy         text,
    lexicon_version  text,
    threshold_version text,
    rule_table_version text,
    model_version    text,
    created_at       timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- mood_logs
-- ---------------------------------------------------------------------------
create table public.mood_logs (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references auth.users (id) on delete cascade,
    mood       smallint not null check (mood between 1 and 5),
    note       text,
    created_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- memory_items: user-visible, editable, deletable
-- ---------------------------------------------------------------------------
create table public.memory_items (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references auth.users (id) on delete cascade,
    content    text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- crisis_resources: NO user PII; starts empty; humans populate. No FK to users.
-- ---------------------------------------------------------------------------
create table public.crisis_resources (
    id           uuid primary key default gen_random_uuid(),
    country_code text,
    language     text,
    name         text not null,
    phone        text,
    url          text,
    notes        text,
    is_active    boolean not null default true,
    created_at   timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- audit_log: append-only (server-side writes via service role)
-- ---------------------------------------------------------------------------
create table public.audit_log (
    id         uuid primary key default gen_random_uuid(),
    user_id    uuid not null references auth.users (id) on delete cascade,
    event_type text not null,
    detail     jsonb,
    created_at timestamptz not null default now()
);

-- ===========================================================================
-- Row Level Security
-- ===========================================================================

alter table public.profiles         enable row level security;
alter table public.consents         enable row level security;
alter table public.conversations    enable row level security;
alter table public.messages         enable row level security;
alter table public.analyses         enable row level security;
alter table public.mood_logs        enable row level security;
alter table public.memory_items     enable row level security;
alter table public.crisis_resources enable row level security;
alter table public.audit_log        enable row level security;

-- profiles: id IS the user id
create policy profiles_select on public.profiles
    for select using (auth.uid() = id);
create policy profiles_insert on public.profiles
    for insert with check (auth.uid() = id);
create policy profiles_update on public.profiles
    for update using (auth.uid() = id) with check (auth.uid() = id);
create policy profiles_delete on public.profiles
    for delete using (auth.uid() = id);

-- consents
create policy consents_select on public.consents
    for select using (auth.uid() = user_id);
create policy consents_insert on public.consents
    for insert with check (auth.uid() = user_id);
create policy consents_update on public.consents
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy consents_delete on public.consents
    for delete using (auth.uid() = user_id);

-- conversations
create policy conversations_select on public.conversations
    for select using (auth.uid() = user_id);
create policy conversations_insert on public.conversations
    for insert with check (auth.uid() = user_id);
create policy conversations_update on public.conversations
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy conversations_delete on public.conversations
    for delete using (auth.uid() = user_id);

-- messages
create policy messages_select on public.messages
    for select using (auth.uid() = user_id);
create policy messages_insert on public.messages
    for insert with check (auth.uid() = user_id);
create policy messages_update on public.messages
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy messages_delete on public.messages
    for delete using (auth.uid() = user_id);

-- analyses
create policy analyses_select on public.analyses
    for select using (auth.uid() = user_id);
create policy analyses_insert on public.analyses
    for insert with check (auth.uid() = user_id);
create policy analyses_update on public.analyses
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy analyses_delete on public.analyses
    for delete using (auth.uid() = user_id);

-- mood_logs
create policy mood_logs_select on public.mood_logs
    for select using (auth.uid() = user_id);
create policy mood_logs_insert on public.mood_logs
    for insert with check (auth.uid() = user_id);
create policy mood_logs_update on public.mood_logs
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy mood_logs_delete on public.mood_logs
    for delete using (auth.uid() = user_id);

-- memory_items
create policy memory_items_select on public.memory_items
    for select using (auth.uid() = user_id);
create policy memory_items_insert on public.memory_items
    for insert with check (auth.uid() = user_id);
create policy memory_items_update on public.memory_items
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy memory_items_delete on public.memory_items
    for delete using (auth.uid() = user_id);

-- crisis_resources: readable by any authenticated user; no client writes.
create policy crisis_resources_select on public.crisis_resources
    for select to authenticated using (is_active = true);

-- audit_log: a user may read their own entries. No client insert/update/delete;
-- server writes via the service role, which bypasses RLS.
create policy audit_log_select on public.audit_log
    for select using (auth.uid() = user_id);

commit;