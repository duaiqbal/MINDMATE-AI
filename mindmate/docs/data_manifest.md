# Data manifest

Every dataset and knowledge source used by MindMate. Licenses are taken from the
official dataset cards (links below), not assumed.

## Labels (model target, fixed)

`joy`, `sadness`, `fear_anxiety`, `anger`, `neutral`

## Languages (kept separate, never pooled)

`en`, `roman_ur`

## Processed schema (JSONL, one file per language)

| column     | notes                                          |
| ---------- | ---------------------------------------------- |
| `text`     | sample text                                    |
| `label`    | one of the 5 core labels                       |
| `language` | `en` or `roman_ur`                             |
| `source`   | `goemotions` or `ruemocorp`                    |
| `split`    | `train` / `val` / `test` (test is frozen)      |

Pipeline: `ml/data/fetch_datasets.py` (download + sha256) ->
`ml/data/prepare_datasets.py` (label mapping, cleaning, splits, freeze) ->
`ml/data/processed/`. Label mapping is human-editable in
`ml/data/label_maps.yaml`. Raw and processed files are git-ignored; checksums
make them reproducible.

## Emotion datasets

### GoEmotions (English)

- Source: google-research/google-research `goemotions/data` (master).
  Card: https://huggingface.co/datasets/google-research-datasets/go_emotions
- License: **Apache-2.0** (stated on the card and the repository LICENSE).
- Annotation: crowdsourced, 3 annotators per comment, English Reddit comments.
- Citation: Demszky et al., "GoEmotions: A Dataset of Fine-Grained Emotions", ACL 2020.
- Mapping: 27 fine labels -> official Ekman groups (`ekman_mapping.json`) ->
  core labels. `disgust` and `surprise` are dropped. A comment is kept only if
  all its labels map to the same core label.
- Result: 44,029 kept; 7,646 excluded (dropped label); 2,588 excluded
  (conflicting labels). Original train/dev/test splits are preserved.
- Known issues:
  - **Strong imbalance**: `fear_anxiety` has only 541 train / 72 val / 80 test.
    Training must use class weighting; report per-class F1, not only accuracy.
  - The official "joy" group also includes approval, admiration, caring,
    desire and pride, which is broader than "joy". A reviewer may tighten it.
  - Reddit text, crowdworkers from one country: cultural and topical bias.
  - The `raw` HF config contains usernames; we use the GitHub TSVs, which hold
    only text, label ids and comment ids.

### RUEmoCorp (Roman Urdu)

- Source: https://huggingface.co/datasets/Inferencelab/RUEmoCorp, file
  `RUEmoCorpus.csv` at pinned revision `8fc7f53e2571b4e0894041d25d197a2a9b6a8dfd`.
- License: card metadata says **CC-BY-4.0**; a README badge says Apache-2.0.
  We follow the stricter **CC-BY-4.0** (attribution required) and cite it.
- Annotation: expert annotators from Pakistani universities; IAA on a
  700-sample benchmark reported as Fleiss' kappa 0.659 (from the card).
- Only the **human-annotated** file is used. The model-labelled "silver" file is
  deliberately excluded.
- Mapping: `happy -> joy`, `sad -> sadness`, `fear -> fear_anxiety`,
  `anger -> anger`, `none -> neutral`; `disgust` and `surprise` dropped.
- Result: 19,575 kept; 8,000 excluded (dropped label); 427 duplicates removed.
  Classes are balanced (~3,000 train each).
- The source has no split. We use a deterministic hash split (80/10/10 on the
  normalized text), so duplicates can never leak between train and test.
- Known issues: social media / WhatsApp text; spelling varies a lot.
  The associated public model reports very high scores; our numbers on our own
  split may differ and must be reported as measured.

## Frozen test sets

Frozen before any training. If a hash changes, the freeze is broken and all
reported test numbers are void.

| language | file | rows | sha256 |
| -------- | ---- | ---- | ------ |
| en | `emotion_en.test.FROZEN.jsonl` | 4,404 | `74ddacdd5a556da270772c65ac55b71a64efeed66f1a86c286f59978d04bd053` |
| roman_ur | `emotion_roman_ur.test.FROZEN.jsonl` | 1,953 | `ba6e5fbae3be6bb3d293afcfeaa476adb900aa5ef7871223acae0cc327969eeb` |

Label maps version: `label-maps-0.1.0`.

## Knowledge sources

### DSM-5 (`dsm5.pdf`, project root)

- Status: **license owner-confirmed** by the project team (FYP owners). The
  agent could not verify it independently; a copy of the permission or
  institutional access note can be attached here.
- Found in the project: the PDF only. No separate DSM-5 dataset file exists in
  the repository.
- Allowed use: **reference context only** (general, non-diagnostic
  psychoeducation background for the knowledge base).
- Not allowed: generating diagnoses, condition labels, criteria checklists, or
  any "you have X" output. The output validator blocks such replies regardless
  of retrieved context.
- Not used as emotion training data (it is not labelled emotion text).