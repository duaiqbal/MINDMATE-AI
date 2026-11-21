# Product: MindMate AI

MindMate is a non-diagnostic, multilingual well-being chat web app. Final Year
Project, University of Haripur. Delivery scope is a **thin slice** (decided).

## What MindMate is

A wellness support tool. It helps a user reflect on how they feel and nudges
them toward their own insight. It is a companion, not a clinician.

## Hard product rules (non-negotiable)

- **Never diagnoses.** No condition labels, ever (no "you have depression",
  "this is anxiety disorder", etc.).
- **Never gives medication or treatment advice.**
- **Never states an unstated cause.** It must not assert a cause (e.g. trauma,
  a relationship, an event) that the user did not themselves state.
- **Insights are offered as questions.** They are hedged, user-correctable, and
  must show the evidence they are based on. The user can always say "that's
  wrong" and the system accepts the correction.

## Languages

- Supported: `en` (English), `roman_ur` (Roman Urdu). Urdu script (`ur`) was removed from scope.
- The app replies in the user's language. Do not switch a user from
  Roman Urdu to English (or vice versa) unless they do.

## Safety (independent layer)

- `backend/app/safety` is independent and **must NEVER import from
  `backend/app/llm`**. A test must fail if that import ever appears.
- The crisis path returns a **fixed, pre-written response**. The LLM is **not**
  called on the crisis path.
- Helplines are read from the `crisis_resources` table. **Never hard-code or
  invent phone numbers**, URLs, or helpline names in code, tests, or docs.

## Uncertainty

- Every classifier output carries a **calibrated confidence**.
- Low confidence routes to the **"clarify"** strategy (ask the user), never to a
  guess presented as fact.

## Strategy selection

- The choice of response strategy comes from `config/reasoning_rules.yaml`, an
  auditable decision table. Strategy logic is data, not scattered `if`s.

## Content authoring boundary

- Do **not** generate crisis lexicon entries or crisis test items. Build the
  loaders, schemas, and tests; **humans author and review** the actual content.

## Honesty about unknowns

- Never invent datasets, licenses, papers, helplines, or free-tier limits.
- Mark anything unconfirmed as **"UNVERIFIED"** in `docs/data_manifest.md`.

## Scope

**IN (thin slice):**

- Safety layer
- Language ID + Roman Urdu normalizer
- Emotion classifier — 5 labels: `joy`, `sadness`, `fear_anxiety`, `anger`,
  `neutral` — with calibration
- Uncertainty gate
- YAML decision table (reasoning rules)
- Constrained LLM reply + output validator + template fallback
- Consent
- User-visible memory
- Export / delete (data rights)
- Mood log + simple trend

**OPTIONAL (only later, only if time allows):**

- RAG, journal, insights panel, distortion tagger (rules-only)

**OPTIONAL / LAST PRIORITY (final reqs):**

- Voice messaging (record -> speech-to-text -> text chat) and a voice-call
  interface (user speaks, reply is text). Non-real-time. Roman Urdu STT
  accuracy is limited and not guaranteed; documented as such.

**OUT:**

- Native mobile, clinical diagnosis, condition labels, trauma inference,
  treatment/medication advice.

## Cut line

If behind schedule **after the emotion-model phase**, drop everything optional
and ship the thin slice.
