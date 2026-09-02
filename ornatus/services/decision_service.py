"""Persists AgentDecision records — observability for what the agent did on
a given run, not a place for chain-of-thought. Callers are expected to pass
an already-concise ``reasoning_summary``.
"""

from ornatus.models._util import new_id
from ornatus.models.decision import AgentDecision, DecisionOutcome, DecisionType
from ornatus.persistence.repositories.agent_decision_repository import AgentDecisionRepository


class DecisionService:
    def __init__(self, repository: AgentDecisionRepository):
        self._repository = repository

    def record(
        self,
        user_id: str,
        user_request: str,
        decision_type: DecisionType,
        tools_used: list[str],
        reasoning_summary: str,
        selected_item_ids: list[str] | None = None,
        excluded_item_ids: list[str] | None = None,
        outcome: DecisionOutcome = DecisionOutcome.COMPLETED,
    ) -> AgentDecision:
        decision = AgentDecision(
            id=new_id("dec"),
            user_id=user_id,
            user_request=user_request,
            decision_type=decision_type,
            tools_used=tools_used,
            selected_item_ids=selected_item_ids or [],
            excluded_item_ids=excluded_item_ids or [],
            reasoning_summary=reasoning_summary,
            outcome=outcome,
        )
        return self._repository.add(decision)

    def list_for_user(self, user_id: str) -> list[AgentDecision]:
        return self._repository.list_for_user(user_id)
