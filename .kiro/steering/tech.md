# Tech

## Backend

- Python 3.11+
- FastAPI
- Pydantic (settings + models)
- pytest
- ONNX Runtime (CPU build only)

## Database & Auth

- Supabase Postgres.
- **Row Level Security on EVERY user table.** No exceptions.
- `pgvector` available (used later for RAG, optional).
- The backend verifies the Supabase JWT and queries **with the user's token**
  so RLS applies.
- The **service-role key lives only on the server**, never in the client.

## Frontend

- React + Vite + TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts (charts)
- Framer Motion (motion)
- react-i18next (i18n; `en` + `roman_ur`, both LTR)
- TanStack Query (server state)
- supabase-js (client)
- MSW (Mock Service Worker) for API mocks

## Hardware & training

- Free tools only.
- Dev machine is **CPU-only (no CUDA)**.
- **All training happens in Colab/Kaggle notebooks** under `ml/notebooks`.
- Only **quantized ONNX inference** runs locally.
- Do **not** install CUDA builds or local LLM weights.

## LLM access

- All LLM calls go through **one module**: `backend/app/llm/gateway.py`.
- The gateway owns: timeout, retry/backoff, and model name (from config).
- It receives **only PII-masked text**.
- It has **no tool access**.

## Secrets

- Secrets live **only in environment variables**.
- Commit `.env.example`. **Never** commit `.env`.

## Dependencies

- No new dependency without a one-line reason.
- **Pin versions.**
- Confirm any library API or model name from official docs; explicitly list
  anything you are unsure of.

## Testing & logging

- **Test-first.** Every task ships with pytest/vitest tests and a verification
  command.
- Log the lexicon version, threshold values, rule-table version, and model
  version for each analysis (reproducibility).

## Evaluation rules

- **Freeze test sets before final training.**
- Tune thresholds on the **validation** split only.
- Report metrics **per language** (`en`, `roman_ur`), with sample sizes and 95% confidence
  intervals.
- **Never pool languages** into one headline number.
