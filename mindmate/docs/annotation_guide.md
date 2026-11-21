# Annotation guide (human-authored)

This guide is for the PEOPLE labelling emotion data. Code does not generate
labels or content; humans decide them using this guide.

## The 5 labels

- **joy** — happiness, contentment, gratitude, hope, relief.
- **sadness** — low mood, grief, loneliness, disappointment.
- **fear_anxiety** — worry, nervousness, panic, dread, feeling unsafe.
- **anger** — frustration, irritation, resentment, rage.
- **neutral** — factual/greeting/no clear emotion.

## How to label

1. Read the whole message, not single words.
2. Choose the **single strongest** emotion. If genuinely none, use `neutral`.
3. Label the emotion the **writer expresses**, not what you feel.
4. Do NOT infer a cause or a diagnosis. Label the feeling only.
5. If unsure between two, pick the stronger; note the ambiguity.

## Language rules

- Label in the sample's own language. Keep `en`, `roman_ur`
  separate.
- Roman Urdu = Urdu written in Latin letters (e.g. "mujhe dar lag raha hai").

## Quality

- At least 2 annotators per sample where possible; record disagreements.
- Keep a small "gold" set checked by a senior reviewer.

## Safety boundary

- This guide covers EMOTION labels only. Crisis phrases are a SEPARATE,
  human-authored safety lexicon and are not created here.