"""User feedback on a recommendation — the Phase 1 memory/preference signal.

Deliberately just a record, not a preference-learning engine: it's the seam
``ornatus.models.preferences.Preferences`` can later be updated from, not a
replacement for it.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class PreferenceSignal(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    NEUTRAL = "neutral"


class Feedback(BaseModel):
    id: str
    user_id: str
    recommendation_id: str | None = None
    feedback_text: str
    rejected_item_ids: list[str] = Field(default_factory=list)
    preference_signal: PreferenceSignal = PreferenceSignal.NEUTRAL
    created_at: datetime = Field(default_factory=utc_now)
