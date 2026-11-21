"""Pipeline tests: history patterns flow into the reply as hedged questions."""

from fastapi.testclient import TestClient

from app.api.chat import get_gateway
from app.chat import respond
from app.emotion.classifier import EmotionPrediction
from app.llm.gateway import GatewayConfig, LlmGateway
from app.longitudinal.patterns import Turn
from app.main import create_app


class StubClassifier:
    """Stands in for the trained model (not available yet)."""

    def __init__(self, label: str, confidence: float):
        self._p = EmotionPrediction(label=label, confidence=confidence)

    def predict(self, text: str) -> EmotionPrediction:
        return self._p


HISTORY = [
    Turn("My boss gave me another deadline", "fear_anxiety", "en"),
    Turn("Nice weather today", "joy", "en"),
]


def _capturing_gateway(reply: str):
    seen: dict = {}

    def provider(model, prompt):
        seen["prompt"] = prompt
        return reply

    return LlmGateway(GatewayConfig(model_name="t"), provider), seen


def test_insight_reaches_prompt_when_confident():
    gw, seen = _capturing_gateway("That sounds heavy. What part is hardest?")
    res = respond(
        "Work deadlines are stressing me out again",
        gateway=gw,
        classifier=StubClassifier("fear_anxiety", 0.9),
        history=HISTORY,
    )
    assert [i.key for i in res.insights] == ["work:fear_anxiety"]
    assert "or am I off" in seen["prompt"]
    assert res.strategy == "reflect"


def test_no_insight_when_unsure_what_user_feels():
    # Low confidence -> clarify. We ask; we do not interpret.
    gw, seen = _capturing_gateway("Can you tell me more?")
    res = respond(
        "Work deadlines again",
        gateway=gw,
        classifier=StubClassifier("fear_anxiety", 0.2),
        history=HISTORY,
    )
    assert res.strategy == "clarify"
    assert res.insights == []
    assert "or am I off" not in seen["prompt"]


def test_dismissed_insight_is_not_offered_again():
    res = respond(
        "Work deadlines are stressing me out again",
        gateway=None,
        classifier=StubClassifier("fear_anxiety", 0.9),
        history=HISTORY,
        dismissed_insights={"work:fear_anxiety"},
    )
    assert res.insights == []


def test_no_history_means_no_insights():
    res = respond("Work is stressful", classifier=StubClassifier("sadness", 0.9))
    assert res.insights == []


def test_endpoint_accepts_history_and_dismissals():
    client = TestClient(create_app())
    r = client.post(
        "/v1/chat",
        json={
            "message": "hello",
            "history": [{"text": "work deadline", "emotion": "anger"}],
            "dismissed_insights": ["work:anger"],
        },
    )
    assert r.status_code == 200
    assert r.json()["insights"] == []


def test_endpoint_rejects_oversized_history():
    client = TestClient(create_app())
    history = [{"text": "x"}] * 201
    r = client.post("/v1/chat", json={"message": "hi", "history": history})
    assert r.status_code == 422


def test_endpoint_override_still_works():
    app = create_app()
    gw = LlmGateway(GatewayConfig(model_name="t"), lambda m, p: "I'm here.")
    app.dependency_overrides[get_gateway] = lambda: gw
    r = TestClient(app).post("/v1/chat", json={"message": "hi"})
    assert r.json()["reply"] == "I'm here."