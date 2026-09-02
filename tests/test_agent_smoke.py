"""End-to-end smoke tests against the real Bedrock/Nova model.

Requires real AWS Bedrock access, so every test here is skipped unless
credentials are present. This is the one place real model behavior is
exercised — the rest of the suite runs against LocalDeterministicModel (see
tests/test_local_agent_workflow.py) and needs no AWS access at all.
"""

import boto3
import pytest

from ornatus.agent.orchestrator import build_orchestrator, build_runtime
from ornatus.api.demo_data import DEMO_USER_ID, seed_demo_wardrobe
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.wardrobe_service import WardrobeService
from ornatus.workflows.decision_logging import run_agent_and_log


def _has_aws_credentials() -> bool:
    try:
        return boto3.Session().get_credentials() is not None
    except Exception:
        # Any failure to resolve credentials (missing config, missing
        # optional botocore extras for a configured provider, etc.) means
        # this environment isn't set up to make a real Bedrock call.
        return False


requires_aws = pytest.mark.skipif(not _has_aws_credentials(), reason="no AWS credentials available")


@requires_aws
def test_agent_answers_from_wardrobe_tool(db):
    seed_demo_wardrobe(WardrobeService(WardrobeRepository(db)))
    agent = build_orchestrator(db=db)

    result = agent(f"What's in {DEMO_USER_ID}'s wardrobe? List item ids only.")

    tool_names_used = {
        block["toolUse"]["name"]
        for message in agent.messages
        for block in message.get("content", [])
        if "toolUse" in block
    }
    assert "get_wardrobe_items" in tool_names_used
    assert "item-blazer-navy" in str(result)


@requires_aws
def test_agent_recommends_outfit_for_client_dinner(tmp_path, monkeypatch):
    monkeypatch.setenv("ORNATUS_DB_PATH", str(tmp_path / "smoke.db"))
    from ornatus.config.settings import get_settings

    get_settings.cache_clear()
    runtime = build_runtime()
    seed_demo_wardrobe(runtime.wardrobe_service)

    result = run_agent_and_log(
        runtime.agent,
        runtime.decision_service,
        runtime.user_id,
        "What should I wear to my client dinner Friday?",
    )

    assert "record_outfit_recommendation" in result.decision.tools_used
    assert result.decision.selected_item_ids
    for item_id in result.decision.selected_item_ids:
        assert runtime.wardrobe_service.get_item(item_id) is not None

    get_settings.cache_clear()
