from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class MemoryType(StrEnum):
    EPISODIC = "episodic"  # summarized interaction log
    LEARNED = "learned"  # distilled signal not yet folded into Preferences


class AgentMemoryEntry(BaseModel):
    id: str
    user_id: str
    memory_type: MemoryType
    content: str
    source_event_ref: str | None = None
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=utc_now)
    superseded_by: str | None = None
