from ornatus.services.calendar_service import CalendarService
from ornatus.services.weather_service import WeatherService
from ornatus.tools.context_tools import make_context_tools


def test_get_event_context_tool_returns_structured_occasion():
    get_event_context, _ = make_context_tools(CalendarService(), WeatherService())

    result = get_event_context(query="client dinner Friday")

    assert result["occasion"] == "client dinner"
    assert "formality" in result
    assert "start_time" in result


def test_get_weather_tool_returns_structured_snapshot():
    _, get_weather = make_context_tools(CalendarService(), WeatherService())

    result = get_weather(location="Downtown", on_date="2026-09-04")

    assert result["location"] == "Downtown"
    assert result["date"] == "2026-09-04"
    assert "condition" in result
    assert "temperature_high_f" in result
