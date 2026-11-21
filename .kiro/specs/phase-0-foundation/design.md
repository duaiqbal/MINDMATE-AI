# Phase 0 — Foundation: Design

This phase produces a skeleton only. The design below describes the shape of the
skeleton, not business logic.

## 1. Repository layout

Follows `.kiro/steering/structure.md`. Top-level `mindmate/` with `backend/`,
`ml/`, `frontend/`, `supabase/`, and `docs/`. Root holds `.gitignore`,
`.env.example`, `README.md`, and `.github/workflows/`.

### .env.example (names only, placeholder values)

```
# Backend
APP_ENV=development
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=   # server only; never shipped to client
SUPABASE_JWT_SECRET=
LLM_MODEL_NAME=              # resolved later; gateway reads this
LLM_TIMEOUT_SECONDS=
# Frontend (Vite — only VITE_* is exposed to the browser)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=
```

No real secrets are committed. `.env` is git-ignored.

## 2. Backend app shell

```
backend/app/
  main.py            # FastAPI app factory, registers /health
  config.py          # Pydantic BaseSettings loaded from env
  api/health.py      # GET /health -> {"status": "ok"}
  safety/__init__.py      # empty; guarded against importing llm
  language/__init__.py
  emotion/__init__.py
  reasoning/__init__.py
  llm/__init__.py
  llm/gateway.py     # stub signature only (no network call in Phase 0)
  validator/__init__.py
  longitudinal/__init__.py
  db/__init__.py
backend/config/        # reasoning_rules.yaml placeholder (empty table header)
backend/lexicons/      # empty; human-authored later
backend/tests/
```

- `config.py` uses Pydantic settings; secrets have **no defaults** so a missing
  value fails fast.
- `gateway.py` exists as a typed stub to anchor the "one LLM module" rule; it
  does not call any provider in Phase 0.

## 3. Database schema (migrations)

One migration creating the tables below. All user-owned tables:

- have a `user_id uuid` column referencing `auth.users(id) ON DELETE CASCADE`,
- have **RLS enabled**,
- carry policies restricting `select/insert/update/delete` to
  `auth.uid() = user_id`.

| Table             | Owner-scoped | Notes                                                   |
| ----------------- | ------------ | ------------------------------------------------------- |
| `profiles`        | yes          | 1 row per user; `id = auth.users.id`                    |
| `consents`        | yes          | consent records (type, granted_at, revoked_at)          |
| `conversations`   | yes          | chat sessions                                           |
| `messages`        | yes          | belongs to a conversation + user                        |
| `analyses`        | yes          | classifier output + versions (lexicon/threshold/model)  |
| `mood_logs`       | yes          | mood entries + timestamp                                |
| `memory_items`    | yes          | user-visible memory (editable/deletable)                |
| `crisis_resources`| no PII       | helplines; **starts empty**, humans populate            |
| `audit_log`       | yes (+system)| append-only audit; policy decided in safety phase       |

- `crisis_resources` holds **no user PII** and **no invented phone numbers**.
  Read policy finalized in the safety phase; Phase 0 leaves it empty.
- `audit_log` is append-only; write/visibility policy is designed in a later
  phase. Phase 0 only creates the table + enables RLS.

Version columns on `analyses` support the reproducibility rule in `tech.md`.

## 4. Foundational tests

- **`test_safety_does_not_import_llm`** — walks every `.py` under
  `backend/app/safety`, parses imports (AST), asserts none resolve to
  `app.llm` / `backend.app.llm`. Passes on the empty skeleton.
- **`test_health`** — boots the app, GET `/health`, asserts `200` +
  `{"status": "ok"}`.
- **Cross-user isolation plan** — `test_rls_isolation.py` written with two test
  users attempting to access each other's rows; marked `skip`/`xfail` with a
  reason until a test Supabase project + users exist.

## 5. Frontend scaffold

```
frontend/src/
  main.tsx, App.tsx
  i18n/            # i18next init + en/ur/roman_ur message catalogs (stub keys)
  theme/tokens.css # design tokens as CSS variables
  consent/ chat/ mood/ dashboard/ memory/ settings/   # placeholder folders
  mocks/           # MSW handlers + browser/server setup
```

- i18next configured for `en`, `ur`, `roman_ur`.
- Direction: `ur` → `dir="rtl"`; `en` and `roman_ur` → `dir="ltr"`. A hook sets
  `<html dir>` and `lang` on locale change.
- Tokens exposed both as CSS variables and mapped into the Tailwind theme so
  `bg-surface`, `text-ink`, etc. work.

### Design tokens

| Token          | Hex       | Role                       |
| -------------- | --------- | -------------------------- |
| `bg`           | `#FAF7F2` | app background             |
| `surface`      | `#FFFFFF` | cards / surfaces           |
| `ink`          | `#2B2A28` | primary text               |
| `ink-muted`    | `#5E5B56` | secondary text             |
| `primary`      | `#4A6B58` | primary action / brand     |
| `primary-soft` | `#DCE8E0` | soft primary fill          |
| `accent`       | `#A8553D` | accent / highlight         |
| `sand`         | `#EFE7DB` | subtle fill                |
| `data-blue`    | `#5F7F96` | chart / data series        |

### WCAG contrast report

Ratios computed from the hex values with the WCAG 2.x relative-luminance
formula. AA = 4.5:1 for normal text, 3:1 for large text (≥ 18.66px bold or
≥ 24px) and UI components.

| Foreground   | Background     | Ratio    | Normal text (AA 4.5) | Large / UI (AA 3.0) |
| ------------ | -------------- | -------- | -------------------- | ------------------- |
| ink          | bg             | 13.42:1  | PASS                 | PASS                |
| ink          | surface        | 14.34:1  | PASS                 | PASS                |
| ink-muted    | bg             | 6.33:1   | PASS                 | PASS                |
| ink-muted    | surface        | 6.76:1   | PASS                 | PASS                |
| primary      | bg             | 5.56:1   | PASS                 | PASS                |
| primary      | surface        | 5.94:1   | PASS                 | PASS                |
| accent       | bg             | 4.87:1   | PASS                 | PASS                |
| accent       | surface        | 5.21:1   | PASS                 | PASS                |
| surface (#fff)| primary       | 5.94:1   | PASS                 | PASS                |
| surface (#fff)| accent        | 5.21:1   | PASS                 | PASS                |
| data-blue    | bg             | 3.96:1   | **FAIL**             | PASS                |
| data-blue    | surface        | 4.23:1   | **FAIL**             | PASS                |
| ink          | primary-soft   | 11.38:1  | PASS                 | PASS                |
| ink          | sand           | 11.69:1  | PASS                 | PASS                |
| primary      | primary-soft   | 4.71:1   | PASS                 | PASS                |

#### Findings and corrections

- **`data-blue` on `bg` (3.96:1) and on `surface` (4.23:1) fail AA for normal
  body text.** `data-blue` is intended for **chart series / data viz and large
  headings**, where it meets AA (≥ 3:1 for graphical objects / large text), so it
  is acceptable for those uses. **Rule:** do **not** use `data-blue` for normal
  body text. If a body-text use is needed, darken it to meet 4.5:1 — a candidate
  is `#4A6577` (to be verified in implementation). This exception is recorded
  here per R5.
- All other default text pairings meet AA for normal text.
- `surface` (white) on `primary` and on `accent` confirms white-on-color button
  labels are AA-compliant.

> Note: these ratios are computed from hex only. Final verification during
> implementation should include rendered checks (e.g. axe / browser devtools),
> since full WCAG conformance also depends on font size, weight, and usage. The
> screenshot-derived spacing/layout remains **UNVERIFIED** until the mockup image
> is provided.

## 6. Mock API (MSW)

Handlers return placeholder shapes only:

| Method | Path                  | Mock returns (placeholder)                        |
| ------ | --------------------- | ------------------------------------------------- |
| POST   | `/v1/chat`            | `{ reply, language, strategy, evidence: [] }`     |
| POST   | `/v1/mood`            | `{ id, created_at }`                              |
| GET    | `/v1/mood/trends`     | `{ points: [...], window }`                       |
| GET    | `/v1/memory`          | `{ items: [...] }`                                |
| PATCH  | `/v1/memory`          | `{ item }` (updated)                              |
| DELETE | `/v1/memory`          | `204`                                             |
| GET    | `/v1/export`          | `{ url | blob }` placeholder                      |
| DELETE | `/v1/account`         | `204`                                             |
| GET    | `/v1/crisis-resources`| `{ resources: [ PLACEHOLDER ] }` — no real numbers |

## 7. CI (GitHub Actions)

A workflow (or matrix) running on push + PR:

1. **Lint** — ruff (backend), eslint (frontend).
2. **Tests** — pytest (backend), vitest (frontend).
3. **Dependency audit** — `pip-audit` (backend), `npm audit` (frontend).
4. **Secret scan** — gitleaks (or equivalent) over the repo.

Any failing gate fails the workflow. Exact action versions are pinned and
confirmed against their docs during implementation.
