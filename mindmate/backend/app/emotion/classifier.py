"""Emotion classifier inference (quantized ONNX, CPU only).

Loads a quantized ONNX model + its tokenizer config from ml/export and returns
a calibrated-confidence prediction. Training happens off-machine (Colab/Kaggle);
only inference runs here.

If the model artifacts are absent (as in the current skeleton), the loader
raises ModelNotAvailable. It NEVER fabricates a prediction. Callers should route
"model unavailable" to a safe path (e.g. the reasoning gate's clarify), not a
guess.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.emotion import LABELS

_EXPORT_DIR = Path(__file__).resolve().parents[3] / "ml" / "export"
_DEFAULT_MODEL = _EXPORT_DIR / "emotion_int8.onnx"
MODEL_VERSION_FILE = _EXPORT_DIR / "model_version.txt"


class ModelNotAvailable(RuntimeError):
    """Raised when the ONNX model artifacts are not present."""


@dataclass(frozen=True)
class EmotionPrediction:
    label: str
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)
    model_version: str = "unset"


def model_version() -> str:
    if MODEL_VERSION_FILE.exists():
        return MODEL_VERSION_FILE.read_text(encoding="utf-8").strip()
    return "model-missing"


def softmax(logits: list[float]) -> list[float]:
    import math

    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    total = sum(exps)
    return [e / total for e in exps]


class EmotionClassifier:
    """Thin wrapper around an ONNX Runtime session.

    Kept import-light: onnxruntime is only imported when a model actually loads,
    so the skeleton (and its tests) run without the heavy dependency installed.
    """

    def __init__(self, model_path: Path | None = None):
        self._model_path = model_path or _DEFAULT_MODEL
        self._session = None
        self._version = model_version()

    def _ensure_loaded(self) -> None:
        if self._session is not None:
            return
        if not self._model_path.exists():
            raise ModelNotAvailable(
                f"ONNX model not found at {self._model_path}. "
                "Train + export it in ml/notebooks first (see ml/README)."
            )
        try:
            import onnxruntime as ort  # imported lazily on purpose
        except ImportError as exc:  # pragma: no cover
            raise ModelNotAvailable("onnxruntime not installed") from exc
        self._session = ort.InferenceSession(
            str(self._model_path), providers=["CPUExecutionProvider"]
        )

    def predict_from_logits(self, logits: list[float]) -> EmotionPrediction:
        """Turn raw logits into a calibrated prediction (used in tests too)."""
        probs = softmax(logits)
        scores = dict(zip(LABELS, probs, strict=True))
        best = max(scores, key=scores.__getitem__)
        return EmotionPrediction(
            label=best,
            confidence=scores[best],
            scores=scores,
            model_version=self._version,
        )

    def predict(self, text: str) -> EmotionPrediction:
        """Run the ONNX model on text. Raises ModelNotAvailable if absent."""
        self._ensure_loaded()
        # Real tokenization + session.run wiring is added with the exported
        # model (tokenizer config ships alongside the .onnx). Kept explicit so
        # the skeleton never pretends to predict.
        raise ModelNotAvailable(
            "inference wiring is completed when the exported model + tokenizer "
            "are present; see ml/export/README"
        )