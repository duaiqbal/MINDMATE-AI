"""Convert raw datasets into the MindMate schema (text,label,language,source,split).

Policies (documented in docs/data_manifest.md):
  * GoEmotions: keep a comment only if ALL its labels map to the SAME core label.
    Comments with a dropped label (disgust/surprise) or conflicting labels are
    excluded and counted.
  * RUEmoCorp: human-annotated 28K only (never the model-labelled silver set).
    The source has no split, so a deterministic hash split (80/10/10 on the
    normalized text) is used; identical texts always share a split.
  * Languages are never pooled: one output file per language.
  * The test split is FROZEN: its sha256 is written to stats.json.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "processed"
MAPS = yaml.safe_load((HERE / "label_maps.yaml").read_text(encoding="utf-8"))
_WS = re.compile(r"\s+")


def norm_key(text: str) -> str:
    return _WS.sub(" ", text.strip().lower())


def hash_split(text: str) -> str:
    h = int(hashlib.sha1(norm_key(text).encode("utf-8")).hexdigest(), 16) % 100
    return "train" if h < 80 else "val" if h < 90 else "test"


def prepare_goemotions() -> tuple[list[dict], dict]:
    emotions = (RAW / "goemotions/emotions.txt").read_text(encoding="utf-8").split()
    ekman = json.loads((RAW / "goemotions/ekman_mapping.json").read_text("utf-8"))
    fine_to_ekman = {f: g for g, fines in ekman.items() for f in fines}
    fine_to_ekman["neutral"] = "neutral"
    to_core = MAPS["goemotions"]["ekman_to_core"]

    rows, stats = [], Counter()
    for fname, split in (("train", "train"), ("dev", "val"), ("test", "test")):
        path = RAW / f"goemotions/{fname}.tsv"
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                stats["malformed"] += 1
                continue
            cores, dropped = set(), False
            for i in parts[1].split(","):
                core = to_core.get(fine_to_ekman[emotions[int(i)]])
                if core is None:
                    dropped = True
                else:
                    cores.add(core)
            if dropped:
                stats["excluded_dropped_label"] += 1
            elif len(cores) != 1:
                stats["excluded_conflicting_labels"] += 1
            else:
                rows.append(
                    {
                        "text": parts[0],
                        "label": cores.pop(),
                        "language": "en",
                        "source": "goemotions",
                        "split": split,
                    }
                )
    stats["kept"] = len(rows)
    return rows, dict(stats)


def prepare_ruemocorp() -> tuple[list[dict], dict]:
    mapping = MAPS["ruemocorp"]["label_to_core"]
    rows, stats, seen = [], Counter(), set()
    with (RAW / "ruemocorp/RUEmoCorpus.csv").open(encoding="utf-8", newline="") as f:
        for rec in csv.DictReader(f):
            text = (rec.get("message") or "").strip()
            raw_label = (rec.get("emotion_label") or "").strip().lower()
            stats[f"source_label_{raw_label}"] += 1
            if not text:
                stats["excluded_empty"] += 1
            elif raw_label not in mapping:
                stats["excluded_unknown_label"] += 1
            elif mapping[raw_label] is None:
                stats["excluded_dropped_label"] += 1
            elif norm_key(text) in seen:
                stats["excluded_duplicate"] += 1
            else:
                seen.add(norm_key(text))
                rows.append(
                    {
                        "text": text,
                        "label": mapping[raw_label],
                        "language": "roman_ur",
                        "source": "ruemocorp",
                        "split": hash_split(text),
                    }
                )
    stats["kept"] = len(rows)
    return rows, dict(stats)


def write_jsonl(path: Path, rows: list[dict]) -> str:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    report: dict = {"label_maps_version": MAPS["version"]}
    for name, fn, lang in (
        ("goemotions", prepare_goemotions, "en"),
        ("ruemocorp", prepare_ruemocorp, "roman_ur"),
    ):
        rows, stats = fn()
        test_rows = [r for r in rows if r["split"] == "test"]
        report[lang] = {
            "source": name,
            "processing": stats,
            "per_split_label_counts": {
                s: dict(Counter(r["label"] for r in rows if r["split"] == s))
                for s in ("train", "val", "test")
            },
            "sha256_all": write_jsonl(OUT / f"emotion_{lang}.jsonl", rows),
            "sha256_test_frozen": write_jsonl(
                OUT / f"emotion_{lang}.test.FROZEN.jsonl", test_rows
            ),
        }
    (OUT / "stats.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()