"""Tests for the emotion classifier calibration + model-missing behaviour."""

import pytest

from app.emotion import LABELS
from app.emotion.classifier import (
    EmotionClassifier,
    ModelNotAvailable,
    softmax,
)


def test_softmax_sums_to_one():
    probs = softmax([2.0, 1.0, 0.1, 0.0, -1.0])
    assert abs(sum(probs) - 1.0) < 1e-9
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_predict_from_logits_picks_argmax_with_confidence():
    clf = EmotionClassifier()
    # highest logit is index 0 -> LABELS[0] == "joy"
    pred = clf.predict_from_logits([5.0, 0.0, 0.0, 0.0, 0.0])
    assert pred.label == LABELS[0]
    assert pred.confidence > 0.9
    assert set(pred.scores) == set(LABELS)


def test_predict_raises_when_model_missing():
    clf = EmotionClassifier()
    # No ONNX artifact in the skeleton -> must not fabricate a prediction.
    with pytest.raises(ModelNotAvailable):
        clf.predict("I feel anxious")