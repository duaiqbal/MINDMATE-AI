# Project structure

```text
mindmate/
  backend/
    app/
      api/            # FastAPI routers / endpoints
      safety/         # independent; NEVER imports from app/llm
      language/       # language ID + Roman Urdu normalizer
      emotion/        # 5-label emotion classifier + calibration
      reasoning/      # uncertainty gate + YAML decision table
      llm/            # gateway.py — the ONLY path to the LLM
      validator/      # output validation + template fallback
      longitudinal/   # mood log + trend
      db/             # db access, Supabase client, RLS-aware queries
      rag/            # ONLY if the optional RAG phase starts
    config/           # reasoning_rules.yaml, settings, thresholds
    lexicons/         # lexicon files (human-authored content)
    tests/            # pytest suites
  ml/
    data/             # datasets (tracked by manifest, not invented)
    notebooks/        # Colab/Kaggle training notebooks
    eval/             # evaluation scripts + frozen test sets
    export/           # quantized ONNX export artifacts
  frontend/
    src/
      consent/
      chat/
      mood/
      dashboard/
      memory/
      settings/
  supabase/
    migrations/       # SQL migrations (schema + RLS policies)
  docs/
    decisions/        # decision records
    eval_reports/     # per-language evaluation reports
    data_manifest.md  # datasets, licenses, UNVERIFIED markers
    annotation_guide.md
```

## Notes

- `backend/app/rag/` is created **only if** the optional RAG phase begins.
- `backend/app/safety` is independent of `backend/app/llm`; a test enforces this.
- Human-authored content (lexicons, crisis items, annotation guide) is reviewed
  by people — code only provides loaders, schemas, and tests.
