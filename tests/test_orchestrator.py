import pytest

from ornatus.agent.orchestrator import build_orchestrator
from ornatus.config.settings import get_settings


@pytest.fixture
def local_provider(monkeypatch):
    """Force the orchestrator to build against the deterministic local model
    instead of Bedrock — these tests only check tool wiring, not real model
    behavior, and must not require AWS credentials.
    """
    monkeypatch.setenv("ORNATUS_MODEL_PROVIDER", "local")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_build_orchestrator_wires_all_expected_tools(db, local_provider):
    agent = build_orchestrator(db=db)

    assert set(agent.tool_names) == {
        "get_wardrobe_items",
        "get_wardrobe_item",
        "mark_wardrobe_item_worn",
        "get_event_context",
        "get_weather",
        "record_outfit_recommendation",
        "record_feedback",
    }
