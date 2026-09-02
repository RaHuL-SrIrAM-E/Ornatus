"""Context Ornatus reasons over when recommending an outfit: a specific
calendar occasion, and the weather for it.

Both are deterministic/mock-backed in Phase 1 (see
``ornatus.services.calendar_service`` and ``ornatus.services.weather_service``).
The models here are the stable contract those services return — swapping the
mock implementation for a real calendar/weather integration later changes the
service, not this shape or the tools built on it.
"""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now
from ornatus.models.common import Formality


class WeatherCondition(StrEnum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    WIND = "wind"


class WeatherSnapshot(BaseModel):
    location: str
    date: date
    condition: WeatherCondition
    temperature_high_f: float
    temperature_low_f: float
    precipitation_probability: float  # 0-1
    humidity_percent: float | None = None
    generated_at: datetime = Field(default_factory=utc_now)


class OccasionContext(BaseModel):
    """A specific calendar occasion the user needs to dress for.

    Distinct from ``ornatus.models.events.EventContext``, which is a
    generic trigger-log entry for the proactive/event-driven layer (weather
    changed, a delivery updated, ...). This model answers "what is the user
    doing, when, and how dressed-up does it need to be" for outfit reasoning.
    """

    id: str
    title: str
    occasion: str
    start_time: datetime
    location: str | None = None
    formality: Formality
    notes: str | None = None
