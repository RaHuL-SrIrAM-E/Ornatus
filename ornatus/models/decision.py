"""Observability record for a single agent run — what was asked, which
tools it used, and what it concluded. Not a chain-of-thought log: only a
concise, application-facing summary is stored.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class DecisionType(StrEnum):
    OUTFIT_RECOMMENDATION = "outfit_recommendation"
    FEEDBACK = "feedback"
    OTHER = "other"


class DecisionOutcome(StrEnum):
    COMPLETED = "completed"
    NO_ACTION = "no_action"
    ERROR = "error"


class AgentDecision(BaseModel):
    id: str
    user_id: str
    user_request: str
    decision_type: DecisionType
    tools_used: list[str] = Field(default_factory=list)
    selected_item_ids: list[str] = Field(default_factory=list)
    excluded_item_ids: list[str] = Field(default_factory=list)
    reasoning_summary: str
    outcome: DecisionOutcome = DecisionOutcome.COMPLETED
    created_at: datetime = Field(default_factory=utc_now)
