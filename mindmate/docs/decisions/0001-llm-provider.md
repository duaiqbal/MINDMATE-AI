# 0001 — LLM provider: OpenRouter with a model fallback chain

Status: accepted. Date: 2026-11-21.

## Decision

Replies are generated through OpenRouter (`https://openrouter.ai/api/v1`) with
this chain, configured in `backend/.env`:

1. `google/gemma-4-31b-it:free` (primary)
2. `google/gemma-4-26b-a4b-it:free`
3. `baidu/ernie-5.5-flash-preview:free`

Every request sets `provider.data_collection = "deny"`, so OpenRouter only
routes to providers that do not collect user data. The model that actually
answered is logged per reply (`llm_model_used`).

## Why

- Groq was ruled out by the project owners.
- Gemini free tier: Google's terms say free-tier content may be used to improve
  Google products, and the model is not open-weight. Not suitable for
  mental-health conversations.
- Hugging Face Inference Providers: no free monthly credits for free accounts.
- Local Ollama: conflicts with `tech.md` ("no local LLM weights") and would be
  slow on the CPU-only laptop.
- OpenRouter: free open-weight models, OpenAI-compatible API, per-request
  privacy routing.

## Verified facts (2026-11-21)

- Gemma 4 31B-it: Apache 2.0 license, open weights, 140+ languages
  (Hugging Face model card).
- OpenRouter does not store prompts unless the account opts in
  (OpenRouter privacy docs); `data_collection: "deny"` is a documented
  routing option.
- Live probe: both Gemma free models returned HTTP 429 (upstream busy);
  NVIDIA free models returned 404 under our privacy filter (their providers
  train on data); ERNIE 5.5 Flash answered in fluent Roman Urdu.

## Not verified / risks

- **ERNIE 5.5 Flash license: UNVERIFIED** (Hugging Face page returned 401).
  It is a "preview" model and may be removed. Report replies it produced
  separately in evaluation.
- Free-model daily limits (third-party sources report 50 requests/day without
  purchased credits) and whether a 429 attempt counts toward them.
- Reply quality in Roman Urdu has not been evaluated yet.