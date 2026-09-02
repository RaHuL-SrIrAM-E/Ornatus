"""Model provider selection/configuration — no AWS calls made or required.

The "bedrock" branch is checked by monkeypatching the BedrockModel class
itself, so this never touches real AWS credentials or the network.
"""

import pytest

from ornatus.agent.local_model import LocalDeterministicModel
from ornatus.agent.model_provider import get_model
from ornatus.config.settings import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_local_provider_returns_deterministic_model(monkeypatch):
    monkeypatch.setenv("ORNATUS_MODEL_PROVIDER", "local")

    model = get_model()

    assert isinstance(model, LocalDeterministicModel)


def test_bedrock_provider_is_configured_from_settings(monkeypatch):
    captured = {}

    class FakeBedrockModel:
        def __init__(self, *, model_id, region_name):
            captured["model_id"] = model_id
            captured["region_name"] = region_name

    monkeypatch.setattr("strands.models.bedrock.BedrockModel", FakeBedrockModel)
    monkeypatch.setenv("ORNATUS_MODEL_PROVIDER", "bedrock")
    monkeypatch.setenv("ORNATUS_BEDROCK_MODEL_ID", "global.amazon.nova-2-lite-v1:0")
    monkeypatch.setenv("ORNATUS_BEDROCK_REGION", "us-west-2")

    model = get_model()

    assert isinstance(model, FakeBedrockModel)
    assert captured == {"model_id": "global.amazon.nova-2-lite-v1:0", "region_name": "us-west-2"}


def test_unsupported_provider_raises(monkeypatch):
    monkeypatch.setenv("ORNATUS_MODEL_PROVIDER", "not-a-real-provider")

    with pytest.raises(Exception):
        get_model()
