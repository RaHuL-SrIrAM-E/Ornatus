"""Deterministic weather lookup.

Phase 1 has no real weather integration — the AWS account this hackathon
runs on is also mid-verification for Bedrock, and a real weather API is out
of scope for this milestone regardless. ``WeatherService.get_weather`` is
the seam a real provider (a weather API client) plugs into later: same
method signature, same ``WeatherSnapshot`` return type, no change needed in
``ornatus.tools.context_tools`` or the agent when that happens.
"""

from datetime import date

from ornatus.models.context import WeatherCondition, WeatherSnapshot

# Small, deterministic "forecast" keyed by weekday. Good enough to make the
# Friday client-dinner scenario (and any other day) behave sensibly without
# a real forecast — not meant to look like real meteorology.
_WEEKDAY_FORECAST: dict[int, dict] = {
    4: dict(  # Friday
        condition=WeatherCondition.CLEAR,
        temperature_high_f=68.0,
        temperature_low_f=52.0,
        precipitation_probability=0.05,
        humidity_percent=45.0,
    ),
}

_DEFAULT_FORECAST = dict(
    condition=WeatherCondition.CLOUDY,
    temperature_high_f=70.0,
    temperature_low_f=58.0,
    precipitation_probability=0.15,
    humidity_percent=55.0,
)


class WeatherService:
    def get_weather(self, location: str, on_date: date) -> WeatherSnapshot:
        forecast = _WEEKDAY_FORECAST.get(on_date.weekday(), _DEFAULT_FORECAST)
        return WeatherSnapshot(location=location, date=on_date, **forecast)
