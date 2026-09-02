from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class OutfitFeedback(StrEnum):
    WORN = "worn"
    REJECTED = "rejected"
    MODIFIED = "modified"
    PENDING = "pending"


class OutfitRecord(BaseModel):
    id: str
    user_id: str
    outfit_date: date
    item_ids: list[str]
    occasion: str | None = None
    weather_summary: str | None = None
    calendar_event_ref: str | None = None
    feedback: OutfitFeedback = OutfitFeedback.PENDING
    rating: int | None = None
    created_at: datetime = Field(default_factory=utc_now)
