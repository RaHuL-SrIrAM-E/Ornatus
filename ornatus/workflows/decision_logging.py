"""Runs the orchestrator for one user request and records what happened.

Decision logging is deliberately application-level, not something the agent
is asked to do via a tool call: it needs to see the whole run (every tool
used), which the model itself isn't guaranteed to self-report accurately —
observability shouldn't depend on the model remembering to report on itself.
"""

from dataclasses import dataclass

from strands import Agent

from ornatus.agent.messages import final_assistant_text, tool_call_names, tool_result_for
from ornatus.models.decision import AgentDecision, DecisionOutcome, DecisionType
from ornatus.services.decision_service import DecisionService

_SUMMARY_LIMIT = 500


@dataclass
class AgentRunResult:
    response_text: str
    decision: AgentDecision


def run_agent_and_log(
    agent: Agent,
    decision_service: DecisionService,
    user_id: str,
    user_request: str,
) -> AgentRunResult:
    try:
        result = agent(user_request)
    except Exception as exc:
        decision_service.record(
            user_id=user_id,
            user_request=user_request,
            decision_type=DecisionType.OTHER,
            tools_used=tool_call_names(agent.messages),
            reasoning_summary=_truncate(f"Run failed: {exc}"),
            outcome=DecisionOutcome.ERROR,
        )
        raise

    messages = agent.messages
    tools_used = list(dict.fromkeys(tool_call_names(messages)))  # de-dup, keep call order
    response_text = final_assistant_text(messages) or str(result)

    if "record_outfit_recommendation" in tools_used:
        recommendation = tool_result_for(messages, "record_outfit_recommendation") or {}
        decision_type = DecisionType.OUTFIT_RECOMMENDATION
        selected_item_ids = recommendation.get("item_ids", [])
        reasoning_summary = recommendation.get("reasoning") or response_text
    elif "record_feedback" in tools_used:
        feedback = tool_result_for(messages, "record_feedback") or {}
        decision_type = DecisionType.FEEDBACK
        selected_item_ids = feedback.get("rejected_item_ids", [])
        reasoning_summary = (
            f"Recorded {feedback.get('preference_signal', 'neutral')} feedback: "
            f"{feedback.get('feedback_text', user_request)}"
        )
    else:
        decision_type = DecisionType.OTHER
        selected_item_ids = []
        reasoning_summary = response_text

    outcome = DecisionOutcome.COMPLETED if tools_used else DecisionOutcome.NO_ACTION

    decision = decision_service.record(
        user_id=user_id,
        user_request=user_request,
        decision_type=decision_type,
        tools_used=tools_used,
        reasoning_summary=_truncate(reasoning_summary),
        selected_item_ids=selected_item_ids,
        outcome=outcome,
    )

    return AgentRunResult(response_text=response_text, decision=decision)


def _truncate(text: str, limit: int = _SUMMARY_LIMIT) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
