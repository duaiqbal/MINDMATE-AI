# MindMate AI

A non-diagnostic, multilingual (English, Urdu script, Roman Urdu) well-being
chat web app. Final Year Project, University of Haripur.

> MindMate is a wellness support tool. It never diagnoses, never labels a user
> with a condition, and never gives medication or treatment advice. See
> `.kiro/steering/product.md` for the full product rules.

## Repository layout

```
mindmate/
  backend/    FastAPI app, config, lexicons, tests
  ml/         data, notebooks, eval, ONNX export
  frontend/   Vite + React + TS app
  supabase/   SQL migrations
  docs/       decisions, eval reports, data manifest
```

See `.kiro/steering/structure.md` for the full tree.

## Prerequisites

- Python 3.11+
- Node.js (LTS) and npm
- Supabase CLI (for local DB + migrations)
- Git

Note: the exact Node version is UNVERIFIED and will be pinned in the frontend task.

## Setup

### 1. Environment variables

```
cp .env.example .env
```

Fill in real values. NEVER commit .env.

### 2. Backend

```
cd mindmate/backend
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e .
pytest
```

(pip installs from pyproject.toml, added in Task 2.)

### 3. Frontend

```
cd mindmate/frontend
npm install
npm run build
```

The Vite dev-server and vitest scripts are defined in package.json (added in Task 5).

### 4. Database (Supabase)

```
cd mindmate
supabase start
supabase db reset
```

## Safety and honesty rules (summary)

- The `backend/app/safety` layer never imports from `backend/app/llm`
  (enforced by a test).
- Crisis responses are fixed and pre-written; the LLM is not called on the
  crisis path. Helplines come from the `crisis_resources` table and are never
  hard-coded or invented.
- Unknowns (datasets, licenses, helplines, free-tier limits) are marked
  UNVERIFIED in `docs/data_manifest.md`.

## Development workflow

Spec-driven, one task at a time. See `.kiro/specs/` for phase specs and
`.kiro/steering/` for product/tech/structure guidance.

