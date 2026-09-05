"""Tests for the FastAPI HTTP layer.

Runs entirely against ``ORNATUS_MODEL_PROVIDER=local`` — no AWS credentials
are needed or used. Exercises the same underlying runtime the CLI uses
(``ornatus.agent.orchestrator``), just reached over HTTP instead of argv.
"""

import pytest
from fastapi.testclient import TestClient

from ornatus.config.settings import get_settings


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("ORNATUS_MODEL_PROVIDER", "local")
    monkeypatch.setenv("ORNATUS_DB_PATH", str(tmp_path / "api-test.db"))
    get_settings.cache_clear()

    from ornatus.api.app import app

    with TestClient(app) as client:
        yield client

    get_settings.cache_clear()


def test_health(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "model_provider": "local"}


def test_chat_outfit_recommendation(api_client):
    response = api_client.post(
        "/chat", json={"message": "What should I wear to my client dinner Friday?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "outfit_recommendation"
    assert body["decision_id"]
    assert body["response"]
    assert body["recommendation"] is not None
    assert body["recommendation"]["item_ids"]
    assert "item-blazer-navy" in body["recommendation"]["item_ids"]


def test_chat_rejects_empty_message(api_client):
    response = api_client.post("/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_rejects_blank_message(api_client):
    response = api_client.post("/chat", json={"message": "   "})
    assert response.status_code == 422


def test_chat_rejects_missing_message_field(api_client):
    response = api_client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_design_request(api_client):
    response = api_client.post(
        "/chat", json={"message": "I want a relaxed cream linen shirt for a summer dinner."}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision_type"] == "design_concept"
    assert body["recommendation"] is None
    assert body["design_concept"] is not None
    spec = body["design_concept"]["garment_specification"]
    assert spec["garment_type"] == "shirt"
    assert spec["fit"] == "relaxed"
    assert spec["material"] == "linen"
    assert "cream" in spec["colors"]


def test_chat_persists_recommendation_and_learns_from_feedback(api_client):
    first = api_client.post(
        "/chat", json={"message": "What should I wear to my client dinner Friday?"}
    )
    assert first.status_code == 200
    assert "item-blazer-navy" in first.json()["recommendation"]["item_ids"]

    feedback = api_client.post(
        "/chat", json={"message": "I like that outfit, but I don't want to wear the blazer."}
    )
    assert feedback.status_code == 200
    assert feedback.json()["decision_type"] == "feedback"

    second = api_client.post(
        "/chat", json={"message": "What should I wear to my client dinner Friday?"}
    )
    assert second.status_code == 200
    recommendation = second.json()["recommendation"]
    assert "item-blazer-navy" not in recommendation["item_ids"]
    assert "item-blazer-navy" in recommendation["excluded_item_ids"]
