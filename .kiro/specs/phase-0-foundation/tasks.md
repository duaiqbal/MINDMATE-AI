# Phase 0 — Foundation: Tasks

Rules: one task at a time; before coding a task, list assumptions and anything
unsure; after each task run its verification command and show the output; do
not mark a task done until its verification command passes.

---

- [ ] 1. Repository bootstrap: folders, `.gitignore`, `.env.example`, README
  - Create the `mindmate/` structure from `structure.md`.
  - Add `.gitignore` (ignores `.env`, `node_modules`, `__pycache__`, build dirs).
  - Add `.env.example` with every env var name + placeholder (no secrets).
  - Write README setup steps (backend, frontend, database).
  - _Acceptance:_ fresh checkout shows the full tree; `.env` is ignored; no
    secret is tracked.
  - _Verification:_ `git status --porcelain` is empty after setup AND
    `git check-ignore .env` prints `.env`.
  - _Requirements:_ R1

- [ ] 2. FastAPI app with `GET /health` and Pydantic settings
  - `main.py` app factory, `config.py` Pydantic settings from env (secrets have
    no defaults), `api/health.py` returning `{"status": "ok"}`.
  - _Acceptance:_ `/health` returns `200` + `{"status":"ok"}`; missing required
    env fails startup with a clear error.
  - _Verification:_ `pytest backend/tests/test_health.py -q` passes.
  - _Requirements:_ R2

- [ ] 3. Supabase migrations: tables + RLS + cascade
  - Migration creating `profiles`, `consents`, `conversations`, `messages`,
    `analyses`, `mood_logs`, `memory_items`, `crisis_resources`, `audit_log`.
  - RLS enabled on every user table; own-rows-only policies; FKs to `auth.users`
    `ON DELETE CASCADE`. `crisis_resources` starts empty.
  - _Acceptance:_ migration applies cleanly; RLS enabled on all user tables;
    cascade FKs present; `crisis_resources` empty.
  - _Verification:_ `supabase db reset` (or `supabase migration up`) succeeds AND
    a SQL check query confirms `rowsecurity = true` for every user table.
    (If no Supabase CLI/project yet: run against a local Postgres/`supabase start`
    — mark blocked and ask, do not fake it.)
  - _Requirements:_ R3

- [ ] 4. Foundational tests: safety-no-llm-import + cross-user isolation plan
  - `test_safety_does_not_import_llm` (AST import scan) — must pass on skeleton.
  - `test_rls_isolation.py` written and collected; `skip`/`xfail` with reason
    until a test Supabase project + two users exist.
  - _Acceptance:_ safety-import test passes; isolation test is collected.
  - _Verification:_ `pytest backend/tests -q` — safety test passes, isolation
    test shows as skipped/xfail (not errored).
  - _Requirements:_ R4

- [ ] 5. Frontend scaffold: Vite + TS + Tailwind + shadcn/ui + i18n + tokens
  - Vite/TS/React app; Tailwind + shadcn/ui; i18next for `en`/`ur`/`roman_ur`
    with RTL for `ur`; tokens as CSS vars + Tailwind theme.
  - Apply the WCAG findings from `design.md` (no `data-blue` for body text).
  - _Acceptance:_ build succeeds; language switcher toggles 3 locales and flips
    to RTL for `ur`; contrast table reflected in token usage.
  - _Verification:_ `npm run build` succeeds AND `npm run test` (vitest) passes a
    test asserting `<html dir="rtl">` for `ur` and `ltr` otherwise.
  - _Note:_ mockup screenshot UNVERIFIED — layout/spacing pending the image.
  - _Requirements:_ R5

- [ ] 6. MSW mock API for all v1 endpoints
  - Handlers for `POST /v1/chat`, `POST /v1/mood`, `GET /v1/mood/trends`,
    `GET|PATCH|DELETE /v1/memory`, `GET /v1/export`, `DELETE /v1/account`,
    `GET /v1/crisis-resources`. Placeholder data only; no invented helplines.
  - _Acceptance:_ each handler returns the documented placeholder shape.
  - _Verification:_ `npm run test` passes a vitest suite exercising every
    handler and asserting response shape.
  - _Requirements:_ R6

- [ ] 7. GitHub Actions: lint, tests, dependency audit, secret scan
  - Workflow running ruff + eslint, pytest + vitest, pip-audit + npm audit,
    gitleaks (or equivalent). Pin action versions (confirm from docs).
  - _Acceptance:_ pipeline passes on the skeleton; a planted dummy secret is
    caught by the scan (then removed).
  - _Verification:_ `act` locally or a push to a branch shows all jobs green;
    secret-scan job flags a temporary dummy secret in a throwaway commit, then
    the commit is reverted.
  - _Requirements:_ R7
