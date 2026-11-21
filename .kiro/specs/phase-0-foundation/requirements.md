# Phase 0 — Foundation: Requirements

## Goal

A runnable skeleton with **no business logic**: the repository, backend app
shell, database schema with RLS, a frontend scaffold, mocked API, foundational
tests, and CI. Everything after this phase builds on this skeleton.

## Out of scope for Phase 0

- Any safety, language, emotion, reasoning, LLM, or longitudinal logic.
- Any real crisis content, lexicons, or helpline data.
- Any model training or inference.

## Assumptions (please confirm)

1. **Mockup screenshot not provided.** Task 5 references "design tokens from the
   attached mockup screenshot," but no image is attached to this session. Phase 0
   uses the explicit hex tokens listed in the brief; the screenshot-derived
   layout/spacing is marked **UNVERIFIED** until you provide the image.
2. The repository root is the current workspace folder; the app lives under a
   top-level `mindmate/` directory per `structure.md`. (Confirm whether you want
   `mindmate/` as a subfolder or the workspace root itself to be the project.)
3. Supabase project/credentials do not exist yet. RLS isolation tests are
   **written and runnable but skipped/xfail** until a test Supabase project and
   two test users exist.
4. Node and Python toolchains are available locally for scaffolding; CI uses
   GitHub Actions.
5. Package manager for frontend is npm (change if you prefer pnpm/yarn).

## Unknowns to resolve (not invented here)

- Supabase project ref, URL, anon key, service-role key — provided later via env.
- Exact helpline data — authored by humans into `crisis_resources`, never here.
- Free-tier limits of any hosting/LLM provider — **UNVERIFIED**.

---

## Requirements (EARS)

### R1 — Repository bootstrap

**User story:** As a developer, I want a clean repository with standard ignore
and environment-example files, so that I can set up the project safely.

- WHEN the repository is cloned, THEN it SHALL contain the folder structure from
  `structure.md`.
- The repository SHALL include a `.gitignore` that excludes `.env`,
  `node_modules`, Python caches, and build artifacts.
- The repository SHALL include a `.env.example` listing every required
  environment variable by name with placeholder values and **no real secrets**.
- The `README` SHALL document setup steps for backend, frontend, and database.
- **Acceptance:** `git status` is clean after a fresh checkout + install (no
  tracked secrets); `.env` is ignored.

### R2 — Backend health endpoint + settings

**User story:** As a developer, I want a running FastAPI app with a health check
and typed settings, so that I can confirm the backend boots.

- WHEN a GET request is made to `/health`, THEN the service SHALL respond `200`
  with a JSON body indicating status `ok`.
- The backend SHALL load configuration from environment variables via a Pydantic
  settings model.
- IF a required environment variable is missing, THEN startup SHALL fail with a
  clear error (no silent defaults for secrets).
- **Acceptance:** `pytest` test hits `/health` and asserts `200` + `{"status":"ok"}`.

### R3 — Database schema with RLS

**User story:** As a user, I want my data isolated from other users, so that no
one else can read or change my rows.

- The migrations SHALL create tables: `profiles`, `consents`, `conversations`,
  `messages`, `analyses`, `mood_logs`, `memory_items`, `crisis_resources`,
  `audit_log`.
- Every user-owned table SHALL have **RLS enabled** with policies that permit a
  user to access **only their own rows**.
- User-owned tables SHALL reference `auth.users` with **ON DELETE CASCADE** so
  deleting an auth user removes their data.
- `crisis_resources` SHALL be readable per the access policy decided later
  (it holds no user PII) and SHALL start **empty** (humans populate it).
- **Acceptance:** migrations apply cleanly; a schema check confirms RLS is
  enabled on every user table and cascade FKs exist.

### R4 — Foundational tests

**User story:** As a maintainer, I want the architectural invariants guarded by
tests, so that regressions fail CI.

- A test SHALL assert that **no module under `backend/app/safety` imports from
  `backend/app/llm`** (static import scan). It SHALL fail if such an import
  exists.
- A **cross-user isolation test plan** SHALL be written and runnable: it attempts
  to read/modify another user's rows and expects denial. It MAY be skipped/xfail
  until a test Supabase project exists, but the test code SHALL exist.
- **Acceptance:** `pytest` runs; the safety-import test passes on the empty
  skeleton; the isolation test is collected (skipped is acceptable in Phase 0).

### R5 — Frontend scaffold

**User story:** As a user, I want an accessible, multilingual UI shell, so that
the app works in English, Urdu, and Roman Urdu.

- The frontend SHALL be a Vite + TypeScript + React app with Tailwind and
  shadcn/ui configured.
- i18n SHALL support `en`, `ur`, `roman_ur`, with **RTL layout for `ur`**.
- Design tokens SHALL be defined as the brief's hex values and exposed as CSS
  variables / Tailwind theme tokens.
- All default text/background pairings SHALL meet **WCAG AA** (≥ 4.5:1 for
  normal text; ≥ 3:1 for large text / UI components). Any pair below AA SHALL be
  corrected and the correction documented.
- **Acceptance:** `npm run build` succeeds; a language switcher toggles all three
  locales and flips direction to RTL for `ur`; the contrast table in `design.md`
  shows every normal-text pair ≥ 4.5:1 (or documents the large-text exception).

### R6 — Mock API (MSW)

**User story:** As a frontend developer, I want mocked endpoints, so that I can
build screens before the backend exists.

- MSW SHALL mock: `POST /v1/chat`, `POST /v1/mood`, `GET /v1/mood/trends`,
  `GET /v1/memory`, `PATCH /v1/memory`, `DELETE /v1/memory`, `GET /v1/export`,
  `DELETE /v1/account`, `GET /v1/crisis-resources`.
- Mock responses SHALL use **placeholder** data only (no invented helplines or
  phone numbers; `/v1/crisis-resources` returns clearly-labeled placeholder
  entries).
- **Acceptance:** a vitest test exercises each handler and asserts the shape of
  the mocked response.

### R7 — CI pipeline

**User story:** As a maintainer, I want CI to enforce quality gates, so that bad
changes are caught before merge.

- GitHub Actions SHALL run: **lint**, **tests** (backend + frontend),
  **dependency audit**, and **secret scan** on push and pull request.
- IF any gate fails, THEN the workflow SHALL fail.
- **Acceptance:** the workflow file(s) exist and the pipeline passes on the
  skeleton; a deliberately planted dummy secret is caught by the secret-scan step
  (verified locally, then removed).
