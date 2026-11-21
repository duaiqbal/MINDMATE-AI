"""Download the raw emotion datasets and record checksums.

Sources (licenses read from the official dataset cards, see docs/data_manifest.md):
  * GoEmotions (English)  - google-research/google-research, Apache-2.0
  * RUEmoCorp (Roman Urdu, human-annotated 28K only) - HF Inferencelab/RUEmoCorp

Raw files go to ml/data/raw/ (git-ignored). Every file's sha256 is written to
ml/data/raw/SHA256SUMS.txt so the exact inputs are reproducible. Standard
library only. The model-labelled "silver" Roman Urdu file is NOT downloaded.
"""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"

GO = "https://raw.githubusercontent.com/google-research/google-research/master/goemotions/data"
RUE_REV = "8fc7f53e2571b4e0894041d25d197a2a9b6a8dfd"
RUE = f"https://huggingface.co/datasets/Inferencelab/RUEmoCorp/resolve/{RUE_REV}"

FILES = {
    "goemotions/train.tsv": f"{GO}/train.tsv",
    "goemotions/dev.tsv": f"{GO}/dev.tsv",
    "goemotions/test.tsv": f"{GO}/test.tsv",
    "goemotions/emotions.txt": f"{GO}/emotions.txt",
    "goemotions/ekman_mapping.json": f"{GO}/ekman_mapping.json",
    "ruemocorp/RUEmoCorpus.csv": f"{RUE}/RUEmoCorpus.csv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    lines = []
    for rel, url in FILES.items():
        dest = RAW / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            print(f"downloading {rel}")
            urllib.request.urlretrieve(url, dest)  # noqa: S310 (fixed https URLs)
        lines.append(f"{sha256(dest)}  {rel}  {dest.stat().st_size} bytes")
    (RAW / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()