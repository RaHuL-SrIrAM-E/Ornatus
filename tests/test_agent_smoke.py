"""End-to-end smoke test: user request -> agent -> tool -> structured data ->
response. Requires real AWS Bedrock access, so it's skipped unless
credentials are present.
"""

import boto3
import pytest

from ornatus.agent.orchestrator import build_orchestrator
from ornatus.api.demo_data import DEMO_USER_ID, seed_demo_wardrobe
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.wardrobe_service import WardrobeService


def _has_aws_credentials() -> bool:
    try:
        return boto3.Session().get_credentials() is not None
    except Exception:
        # Any failure to resolve credentials (missing config, missing
        # optional botocore extras for a configured provider, etc.) means
        # this environment isn't set up to make a real Bedrock call.
        return False


@pytest.mark.skipif(not _has_aws_credentials(), reason="no AWS credentials available")
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
    assert "item-1" in str(result)
