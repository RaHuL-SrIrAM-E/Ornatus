"""Agent-facing tools over CalendarService and WeatherService.

Thin wrappers, same as wardrobe_tools.py: no reasoning here, just
delegation and shape conversion. The mock-vs-real distinction lives entirely
inside the services (see ornatus/services/calendar_service.py and
weather_service.py) — these tool signatures don't change when a real
integration replaces the mock.
"""

from datetime import date

from strands import tool

from ornatus.services.calendar_service import CalendarService
from ornatus.services.weather_service import WeatherService


def make_context_tools(calendar_service: CalendarService, weather_service: WeatherService) -> list:
    @tool
    def get_event_context(query: str) -> dict:
        """Look up occasion/calendar context relevant to a request — what the
        user is doing, when, where, and how dressed-up it needs to be.

        Args:
            query: The user's request or a short description of the occasion
                to look up (e.g. "client dinner Friday").

        Returns:
            An occasion as a structured dict: id, title, occasion,
            start_time (ISO datetime), location, formality, notes.
        """
        occasion = calendar_service.get_occasion(query)
        return occasion.model_dump(mode="json")

    @tool
    def get_weather(location: str, on_date: str) -> dict:
        """Look up the weather forecast for a location and date.

        Args:
            location: Where to check the forecast for.
            on_date: The date to check, as an ISO date string (YYYY-MM-DD).

        Returns:
            A weather snapshot as a structured dict: location, date,
            condition, temperature_high_f, temperature_low_f,
            precipitation_probability, humidity_percent.
        """
        snapshot = weather_service.get_weather(location, date.fromisoformat(on_date))
        return snapshot.model_dump(mode="json")

    return [get_event_context, get_weather]
