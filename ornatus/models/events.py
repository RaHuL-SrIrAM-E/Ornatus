from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class EventType(StrEnum):
    WEATHER = "weather"
    CALENDAR = "calendar"
    TRIP = "trip"
    DELIVERY = "delivery"
    MANUAL = "manual"


class EventContext(BaseModel):
    id: str
    user_id: str
    type: EventType
    payload: dict = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=utc_now)
    processed: bool = False
