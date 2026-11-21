# MindMate AI: An Emotion-Aware Multilingual Conversational AI Companion for Personalized Mental Wellness Support

**Final Year Project — Updated Proposal (reflects the implemented system)**
Department of Information Technology, The University of Haripur

| | |
|---|---|
| Students | Aleesha Iftikhar, Tooba Iqbal |
| Supervisor | ____________________ |
| Repository | https://github.com/duaiqbal/MINDMATE-AI |
| Document status | Updated proposal. Sections marked **Implemented** exist in the codebase with passing tests. Sections marked **Planned** are not built yet. No evaluation results are reported until the model is trained on the frozen test sets. |

---

## 1. Introduction

Stress, anxiety, low mood, loneliness, burnout and academic pressure are common among students and young professionals. Many people do not seek help because of stigma, cost, limited access to services, or not knowing how to describe what they feel. General-purpose chatbots usually give generic replies, do not track how a person's feelings change over time, and handle Roman Urdu poorly.

MindMate AI is a non-diagnostic, multilingual (English and Roman Urdu) wellness companion. It listens like a caring friend, helps the user notice and name their emotions, and offers gentle, correctable reflections about patterns in their own words. It is a self-reflection tool. It does not diagnose, label conditions, or give medication or treatment advice, and it does not replace professional care.

## 2. Problem Statement

1. Existing chatbots do not detect emotion reliably, especially in Roman Urdu, which has no standard spelling.
2. They act on uncertain predictions as if they were facts.
3. They let a language model improvise "therapy-like" replies with no explicit, auditable strategy.
4. They treat every conversation in isolation and miss recurring patterns.
5. Their safety behaviour depends on the same model that generates replies, so it can fail silently.
6. They are rarely evaluated with clear, per-language quantitative metrics.

## 3. Objectives

1. Build a warm, human-friendly conversational companion in English and Roman Urdu.
2. Detect emotions with a transformer model that reports a calibrated confidence for every prediction.
3. Route low-confidence cases to a cautious "clarify" strategy instead of guessing.
4. Select the response strategy from an auditable decision table (data, not hidden code).
5. Support self-discovery: finer emotion nuances and patterns across a conversation, always offered as questions with the user's own words as evidence.
6. Provide mood tracking, user-visible memory, consent, and data export/delete.
7. Keep an independent safety layer that can override the normal flow and is never controlled by the language model.
8. Evaluate every core module with defined metrics, reported per language with 95% confidence intervals.
9. Offer voice input (voice messages and a voice-call interface with text replies).

## 4. Scope

**In scope (thin slice):** safety layer; language identification and Roman Urdu normalization; 5-label emotion classifier with calibration; uncertainty gate; YAML decision table; constrained LLM reply with output validator and template fallback; consent; user-visible memory; export/delete; mood log and trend; emotion nuances and conversation patterns (self-discovery).

**Added by final requirements:** voice messaging and a voice-call interface (user speaks, reply is text). Lowest priority; non-real-time.

**Optional, if time allows:** retrieval-augmented generation (RAG) over a knowledge base; journaling; breathing exercises; cognitive-distortion tagger.

**Out of scope:** clinical diagnosis or condition labels, trauma inference, medication or treatment advice, native mobile apps, Urdu (Nastaliq) script.

## 5. Changes from the Original Proposal

| Original proposal | Current design | Reason |
|---|---|---|
| English, Urdu and Roman Urdu | English and Roman Urdu | Urdu-script emotion data is scarce; two languages give more reliable per-language evaluation within the FYP time. |
| FAISS + LangChain for retrieval | Not used yet. Supabase Postgres (pgvector available) is the planned store for RAG | One database for app data and vectors; RAG is optional and will be decided when that phase starts. |
| SQLite/PostgreSQL | Supabase Postgres with Row Level Security on every user table | Built-in auth, per-user data isolation enforced by the database. |
| No voice | Voice messages + voice-call interface (text replies) | Added in the final requirements. |
| Single emotion level | Two tiers: 5 core labels (model) + finer nuances (rules) | Reliable model target plus richer self-discovery. |

## 6. System Architecture

### 6.1 Message pipeline (Implemented)

Every user message passes through this order. Safety runs first, the LLM runs last, and the validator checks every reply.

```
User message
  -> Normalize (Roman Urdu spelling variants, elongation)
  -> Language ID (en / roman_ur, with confidence)
  -> SAFETY LAYER  --crisis-->  fixed pre-written response + helplines from DB (LLM NOT called)
  -> Emotion classifier (5 labels + calibrated confidence)
  -> Nuance tagger (finer feelings, rule-based)
  -> Reasoning engine (YAML decision table; low confidence -> "clarify")
  -> Pattern detector (recurring topic + difficult feeling across turns)
  -> Prompt builder (warm persona + chosen strategy + evidence)
  -> LLM gateway (PII masked, timeout, retry/backoff)
  -> Output validator (blocks diagnosis, medication, unstated cause) -> template fallback
  -> Reply + provenance (all component versions logged)
```

If any part is missing or fails, the system degrades safely: no emotion model means confidence 0 and the "clarify" strategy; no LLM provider or an LLM error means a safe hedged template; a reply that breaks a rule is replaced by a template.

### 6.2 Components

| Component | Location | Status |
|---|---|---|
| Roman Urdu normalizer | `backend/app/language/normalizer.py` | Implemented |
| Language identifier | `backend/app/language/identifier.py` | Implemented (rule-based) |
| Safety layer | `backend/app/safety/` | Mechanism implemented; crisis phrases and helplines must be written by humans |
| Emotion dataset loader | `backend/app/emotion/dataset.py` | Implemented |
| Emotion classifier (ONNX inference) | `backend/app/emotion/classifier.py` | Loader implemented; trained model pending |
| Nuance tagger | `backend/app/emotion/nuance.py`, `config/emotion_taxonomy.yaml` | Implemented |
| Reasoning engine + uncertainty gate | `backend/app/reasoning/engine.py`, `config/reasoning_rules.yaml`, `config/thresholds.yaml` | Implemented |
| Pattern detector | `backend/app/longitudinal/patterns.py`, `config/pattern_topics.yaml` | Implemented |
| Mood trend | `backend/app/longitudinal/trend.py` | Implemented |
| Persona + prompt builder | `backend/app/chat/persona.py` | Implemented |
| Chat orchestrator | `backend/app/chat/orchestrator.py` | Implemented |
| LLM gateway + PII masking | `backend/app/llm/gateway.py`, `backend/app/llm/pii.py` | Implemented; provider and API key pending |
| Output validator + templates | `backend/app/validator/output_validator.py` | Implemented |
| REST API | `backend/app/api/` | Implemented |
| Database schema + RLS | `supabase/migrations/20250101000000_init_schema.sql` | Implemented and tested on Postgres |
| Frontend | `frontend/src/` | Screens implemented on a mock API |
| Training notebook | `ml/notebooks/emotion_training/` | Implemented; not yet run |
| Cognitive-distortion detector | — | Planned |
| Voice messaging / call | — | Planned |
| RAG knowledge base | — | Planned (optional) |

## 7. Module Details

### 7.1 Language handling (Implemented)

- **Normalizer:** lowercasing, Unicode normalization, punctuation removal, collapsing elongated letters ("yaaaar" -> "yaar"), and mapping common Roman Urdu spelling variants ("nhi", "nai" -> "nahi"). Versioned for reproducibility.
- **Language ID:** distinguishes English and Roman Urdu using common Roman Urdu function words. It returns a confidence; ambiguous or Urdu-script input gets low confidence, which leads to a clarifying question.
- The app replies in the user's language and does not switch languages unless the user does.

### 7.2 Emotion detection (Model pending training)

- **Core labels (model target):** joy, sadness, fear_anxiety, anger, neutral.
- **Model:** XLM-RoBERTa base, fine-tuned on both languages together; evaluation stays per language.
- **Imbalance handling:** class-weighted cross-entropy (English fear_anxiety has only 541 training samples).
- **Calibration:** temperature scaling, fitted on the validation split only.
- **Deployment:** exported to ONNX and quantized to int8 so it runs on a CPU-only machine with ONNX Runtime.
- **Training environment:** Google Colab free T4 GPU. The development laptop (Intel i5-1145G7, 16 GB RAM, Intel Iris Xe) has no CUDA GPU, so local training of a transformer would take many hours.

### 7.3 Self-discovery (Implemented)

- **Nuances:** under each core emotion, finer feelings are detected from everyday words in English and Roman Urdu, for example loneliness, grief, disappointment and hopelessness under sadness; worry, panic, overwhelm and social anxiety under fear_anxiety; frustration, resentment and irritation under anger; gratitude, hope, relief and contentment under joy; calm, tired and mixed under neutral.
- **Conversation patterns:** when a topic the user mentioned (work, studies, family, friends, sleep, money) appears with a difficult feeling in at least two separate messages, MindMate may ask, for example: "I've noticed work came up more than once when you felt worried. Does that match how it feels to you, or am I off?"
- **Rules:** insights are always questions, show the user's own words as evidence, never state a cause, never name a condition, and are only offered when the system is confident about the strategy. If the user says an insight is wrong, it is never shown again.

### 7.4 Psychological reasoning engine (Implemented: strategy table. Planned: distortion detector)

- Strategy selection is a YAML decision table evaluated top to bottom:
  1. Crisis -> `crisis_response`
  2. Confidence below threshold (0.55) -> `clarify`
  3. Confident sadness / fear_anxiety / anger -> `reflect`
  4. Confident joy / neutral -> `support`
- The table and threshold versions are logged with every reply.
- **Planned:** a rules-based cognitive-distortion detector (for example catastrophizing, all-or-nothing thinking) that adds a gentle, question-form reflection strategy. It will not label the user.

### 7.5 Uncertainty-aware processing (Implemented)

Every classification carries a confidence. Low confidence (common with Roman Urdu) leads to a clarifying question, never to a guess presented as fact. Thresholds are tuned on the validation split only.

### 7.6 Independent safety layer (Mechanism implemented)

- Lives in its own package and must never import the LLM module; an automated test fails if it does.
- Runs before any other analysis. On a crisis match it returns a fixed, pre-written response and does not call the LLM.
- Helplines are read from the `crisis_resources` database table. No phone numbers or helpline names are written in code.
- Crisis phrases and helpline entries must be written and reviewed by people (supervisor or qualified reviewer). The code provides only the loader, schema and tests. With an empty lexicon it never invents a crisis match.

### 7.7 Constrained replies (Implemented)

- **Persona:** warm, natural, like a trusted friend; reflects what it heard and asks one caring follow-up question; no robotic or formal tone.
- **Output validator:** rejects replies that diagnose ("you have depression"), give medication or treatment advice, or assert a cause the user did not state ("this is because of your trauma"). Rejected replies are replaced by a safe, hedged template in the user's language.
- **LLM gateway:** the only path to the language model; receives only PII-masked text (emails, phone numbers, URLs masked); owns timeout, retry with backoff, and model name from configuration; has no tool access. Planned provider: an open-source model (Qwen or Llama) through a free-tier inference API such as Groq. Free-tier limits are not verified yet.

### 7.8 Longitudinal analysis and user features (Implemented)

- Mood log (1–5 scale with optional note) and a per-day average trend.
- User-visible memory: list, add, edit, delete.
- Consent records.
- Data rights: export all data as JSON; delete account and all data.

### 7.9 Voice (Planned)

- **Voice messaging:** record with a microphone button, transcribe to text, then process like a typed message. Typing remains available.
- **Voice-call interface:** the user speaks; replies are shown as text (voice reply not required).
- **Known limitation:** speech-to-text accuracy for Roman Urdu (code-mixed Urdu/English) is limited in all free tools. The speech-to-text option will be chosen by testing, and its measured accuracy will be reported honestly.

### 7.10 Knowledge base and DSM-5 (Planned, optional)

- `dsm5.pdf` is in the project folder. The project owners have confirmed permission to use it.
- It will be used only as background reference for general, non-diagnostic psychoeducation. It will not be used to generate diagnoses, condition labels or criteria checklists, and it is not used as emotion training data. The output validator blocks diagnostic replies regardless of what is retrieved.

## 8. Datasets (Implemented)

| | English | Roman Urdu |
|---|---|---|
| Dataset | GoEmotions (Demszky et al., ACL 2020) | RUEmoCorp (human-annotated file only) |
| License | Apache-2.0 | CC-BY-4.0 (attribution required) |
| Annotation | Crowdsourced, 3 annotators per comment | Expert annotators; reported Fleiss' κ = 0.659 on a 700-sample benchmark |
| Rows kept | 44,029 | 19,575 |
| Excluded | 7,646 (disgust/surprise), 2,588 (conflicting labels) | 8,000 (disgust/surprise), 427 duplicates |
| Train / Val / Test | 35,199 / 4,426 / 4,404 (official splits) | 15,681 / 1,941 / 1,953 (deterministic hash split, no train/test overlap) |

- Label mapping is in `ml/data/label_maps.yaml` and can be reviewed and changed.
- The model-labelled "silver" Roman Urdu file is deliberately excluded.
- Test sets were **frozen before training**; their SHA-256 hashes are recorded in `docs/data_manifest.md`, and both the tests and the training notebook refuse to run if a test set changes.
- Pipeline: `ml/data/fetch_datasets.py` (download + checksums) -> `ml/data/prepare_datasets.py` (mapping, cleaning, splits, freeze).

**Known data limitations:** strong class imbalance in English (very few fear_anxiety samples); GoEmotions' "joy" group also includes approval, admiration and caring; both datasets come from social media, which introduces cultural and topical bias.

## 9. Database Design (Implemented)

Supabase Postgres. Row Level Security is enabled on every table; users can access only their own rows; deleting a user cascades to all their data.

| Table | Purpose |
|---|---|
| `profiles` | one row per user, preferred locale |
| `consents` | consent type, granted / revoked time |
| `conversations` | chat sessions |
| `messages` | messages with role and language |
| `analyses` | emotion label, confidence, strategy, and lexicon / threshold / rule-table / model versions |
| `mood_logs` | mood 1–5 with note |
| `memory_items` | user-visible memory |
| `crisis_resources` | helplines (no user data; populated by humans) |
| `audit_log` | append-only events (server writes only) |

Verified on a real Postgres instance: RLS enabled on all 9 tables, cascade delete works, and one user cannot read, insert or update another user's rows.

**Pending:** a Supabase project and the database-backed repository (the API currently uses an in-memory store with the same per-user isolation).

## 10. API (Implemented)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness |
| POST | `/v1/chat` | full pipeline; accepts message, history and dismissed insights; returns reply, language, strategy, emotion, confidence, crisis flag, nuances and insights |
| POST | `/v1/mood` | log mood |
| GET | `/v1/mood/trends` | per-day trend (1–90 day window) |
| GET / POST | `/v1/memory` | list / add memory |
| PATCH / DELETE | `/v1/memory/{id}` | edit / delete memory |
| POST / GET | `/v1/consent` | grant / list consent |
| GET | `/v1/export` | export all user data |
| DELETE | `/v1/account` | delete account and data |
| GET | `/v1/crisis-resources` | helplines (mock in the frontend; populated from DB) |

## 11. Frontend (Implemented on a mock API)

- Screens: Consent (shown first), Chat, Mood, Dashboard (mood trend chart), Memory, Settings (language, export, delete).
- English and Roman Urdu interface; language switcher.
- Design tokens with a WCAG contrast check: all text colours pass AA for normal text except the chart colour `data-blue`, which is restricted to charts and large text.
- A mock API (MSW) lets the screens run before the backend is connected.
- **Pending:** connecting to the real backend; showing nuances and insights with a "that's not right" button; voice UI.

## 12. Technology Stack

| Layer | Technologies (pinned versions) |
|---|---|
| Backend | Python 3.11+, FastAPI 0.162.0, Pydantic 2.10.4, pydantic-settings 2.7.0, PyYAML 6.0.2, Uvicorn 0.34.0 |
| Database / Auth | Supabase Postgres, Row Level Security, pgvector (optional) |
| ML | PyTorch and Transformers (Colab-provided versions, recorded in the eval report), XLM-RoBERTa base, ONNX 1.23.2, ONNX Runtime 1.31.1 (CPU) |
| Frontend | React 19.1.1, Vite 8.3.6, TypeScript 5.9.3, Tailwind CSS 4.3.4, TanStack Query 5.106.1, React Router 7.18.5, Recharts 3.10.1, i18next 26.7.2 / react-i18next 17.1.13 |
| Testing | pytest 9.0.3, Vitest 5.1.0, Testing Library, MSW 3.0.3 |
| Quality / CI | GitHub Actions: ruff, ESLint, pytest, Vitest, build, pip-audit, npm audit, gitleaks secret scan |
| LLM (planned) | Qwen or Llama through a free-tier API such as Groq (limits UNVERIFIED) |
| Training | Google Colab free T4 GPU |

## 13. Evaluation Plan (Strict Evaluation Matrix)

All results are reported **separately for English and Roman Urdu**, never pooled into one number, with sample sizes and 95% confidence intervals.

| Module | Metrics |
|---|---|
| Emotion classifier | accuracy (Wilson 95% CI), macro-F1 (bootstrap 95% CI, 1,000 resamples), per-class precision / recall / F1, expected calibration error (ECE) |
| Baseline comparison | char n-gram TF-IDF + logistic regression vs. XLM-R, on the same frozen test sets |
| Language ID | accuracy per language on a labelled sample |
| Safety layer | **recall** on a human-written crisis test set (primary safety metric), plus false-positive rate |
| Output validator | rejection rate on forbidden replies; pass rate on safe replies |
| Uncertainty gate | share of low-confidence cases routed to "clarify"; accuracy above vs. below threshold |
| Voice | word error rate (WER) per language on a small recorded set |

Already automated: the training notebook computes and exports the emotion metrics; current test suites check every rule above at the code level (backend 126 tests, frontend 14 tests).

## 14. Ethics, Safety and Privacy

- No diagnosis, no condition labels, no medication or treatment advice, no stated causes the user did not give. Enforced in the prompt and again by the output validator.
- Insights are questions, show their evidence, and can be rejected by the user.
- Crisis handling is independent of the language model and uses only human-written content.
- Consent is required before use. Users can export or delete all their data.
- Each user's data is isolated by the database (Row Level Security).
- Text sent to the LLM is PII-masked. Secrets live only in environment variables; the service-role key never reaches the browser.
- Dataset licenses are documented and attribution is given. DSM-5 is used only as non-diagnostic reference.
- Emotion detection can be misused for surveillance; MindMate uses it only to help the user reflect on their own feelings.

## 15. Current Status

| Area | Status |
|---|---|
| Project setup, CI, database schema with RLS | Done |
| Language ID, normalizer, reasoning engine, uncertainty gate | Done |
| Safety layer mechanism | Done (content pending) |
| Output validator, LLM gateway, persona, chat pipeline, `/v1/chat` | Done (LLM provider pending) |
| Nuances and conversation patterns | Done |
| Mood, memory, consent, export / delete APIs | Done (in-memory store) |
| Frontend screens | Done (mock API) |
| Datasets prepared, test sets frozen | Done |
| Training notebook | Ready, not yet run |
| Trained model + evaluation report | Pending |
| Cognitive-distortion detector | Pending |
| Crisis content and safety recall evaluation | Pending (needs human-written content) |
| Supabase project + database repository | Pending |
| Frontend connected to backend | Pending |
| Voice messaging and voice call | Pending |
| RAG knowledge base, journaling, breathing exercises | Optional |
| Deployment and final documentation | Pending |

## 16. Remaining Work Plan

Order of work. Durations are estimates.

1. Run the training notebook on Colab (about 1 hour) and connect the model to the app (about half a day).
2. Cognitive-distortion detector (about 1 day).
3. Connect the LLM provider with an API key (2–3 hours).
4. Connect the frontend to the backend, including insights and the "that's not right" action (about 1 day).
5. Supabase project and database-backed repository (about 1 day).
6. Human-written crisis content, then the safety recall evaluation (about 1 day after content exists).
7. Voice messaging and voice-call interface (2–3 days).
8. Optional: RAG knowledge base (about 2 days), journaling and breathing exercises (1–2 days).
9. Deployment, final evaluation report, documentation (about 1 day).

Cut line: if behind schedule after the emotion-model step, optional items are dropped and the core system is delivered.

## 17. Resources Required

- **Hardware:** development laptop (Intel i5-1145G7, 16 GB RAM, no CUDA GPU); Google Colab free T4 GPU for training; stable internet.
- **Software:** listed in Section 12. All tools are free or open source.
- **Services:** Supabase (database and auth), a free-tier LLM inference API, GitHub.
- **Human input:** crisis phrases, helplines and crisis test items written and reviewed by the team and supervisor; review of the label mapping and nuance word lists.

## 18. References

- Demszky, D., Movshovitz-Attias, D., Ko, J., Cowen, A., Nemade, G., & Ravi, S. (2020). GoEmotions: A Dataset of Fine-Grained Emotions. *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL)*.
- RUEmoCorp — Roman Urdu Emotion Corpus. Hugging Face dataset `Inferencelab/RUEmoCorp`, CC-BY-4.0. https://huggingface.co/datasets/Inferencelab/RUEmoCorp
- American Psychiatric Association. *Diagnostic and Statistical Manual of Mental Disorders, Fifth Edition (DSM-5)*. Used as non-diagnostic reference only.

Further literature-review references are to be added by the project team.

---

| Student | Signature | Supervisor Signature |
|---|---|---|
| Aleesha Iftikhar | ____________ | |
| Tooba Iqbal | ____________ | ____________ |