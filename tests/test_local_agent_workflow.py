"""End-to-end local agent workflow test.

Exercises the full loop —
    user -> agent -> tools (context/weather/wardrobe) -> reasoning ->
    outfit recommendation -> decision log -> feedback -> preference signal
— using ``LocalDeterministicModel`` instead of Bedrock, so it requires no
AWS credentials. See ornatus/agent/local_model.py for what that model is
(and is not).
"""

from strands import Agent

from ornatus.agent.local_model import LocalDeterministicModel
from ornatus.agent.system_prompt import SYSTEM_PROMPT
from ornatus.api.demo_data import DEMO_USER_ID, seed_demo_wardrobe
from ornatus.models.decision import DecisionType
from ornatus.services.calendar_service import CalendarService
from ornatus.services.weather_service import WeatherService
from ornatus.tools.context_tools import make_context_tools
from ornatus.tools.feedback_tools import make_feedback_tools
from ornatus.tools.outfit_tools import make_outfit_tools
from ornatus.tools.wardrobe_tools import make_wardrobe_tools
from ornatus.workflows.decision_logging import run_agent_and_log


def _local_agent(wardrobe_service, outfit_service, feedback_service) -> Agent:
    tools = [
        *make_wardrobe_tools(wardrobe_service, DEMO_USER_ID),
        *make_context_tools(CalendarService(), WeatherService()),
        *make_outfit_tools(outfit_service, DEMO_USER_ID),
        *make_feedback_tools(feedback_service, DEMO_USER_ID),
    ]
    return Agent(model=LocalDeterministicModel(), system_prompt=SYSTEM_PROMPT, tools=tools)


def test_outfit_recommendation_end_to_end(wardrobe_service, outfit_service, feedback_service, decision_service):
    seed_demo_wardrobe(wardrobe_service)
    agent = _local_agent(wardrobe_service, outfit_service, feedback_service)

    result = run_agent_and_log(
        agent, decision_service, DEMO_USER_ID, "What should I wear to my client dinner Friday?"
    )

    assert result.decision.decision_type == DecisionType.OUTFIT_RECOMMENDATION
    assert set(result.decision.tools_used) >= {
        "get_event_context",
        "get_weather",
        "get_wardrobe_items",
        "record_outfit_recommendation",
    }
    # The agent chose real wardrobe items, not invented ones.
    assert result.decision.selected_item_ids
    for item_id in result.decision.selected_item_ids:
        assert wardrobe_service.get_item(item_id) is not None
    # Cool Friday evening + business-casual dinner -> the blazer gets picked.
    assert "item-blazer-navy" in result.decision.selected_item_ids
    assert result.response_text

    recommendation = outfit_service.get_latest_for_user(DEMO_USER_ID)
    assert recommendation is not None
    assert recommendation.item_ids == result.decision.selected_item_ids
    assert recommendation.request_text == "What should I wear to my client dinner Friday?"


def test_feedback_end_to_end_after_recommendation(
    wardrobe_service, outfit_service, feedback_service, decision_service
):
    seed_demo_wardrobe(wardrobe_service)
    run_agent_and_log(
        _local_agent(wardrobe_service, outfit_service, feedback_service),
        decision_service,
        DEMO_USER_ID,
        "What should I wear to my client dinner Friday?",
    )

    # A separate agent/conversation, like a second CLI invocation — feedback
    # must be resolved against persisted state, not conversation memory.
    result = run_agent_and_log(
        _local_agent(wardrobe_service, outfit_service, feedback_service),
        decision_service,
        DEMO_USER_ID,
        "I like that outfit, but I don't want to wear the blazer.",
    )

    assert result.decision.decision_type == DecisionType.FEEDBACK
    assert "item-blazer-navy" in result.decision.selected_item_ids

    stored = feedback_service.list_for_user(DEMO_USER_ID)
    assert len(stored) == 1
    assert stored[0].rejected_item_ids == ["item-blazer-navy"]
    assert stored[0].recommendation_id == outfit_service.get_latest_for_user(DEMO_USER_ID).id
