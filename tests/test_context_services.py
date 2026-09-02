from datetime import date

from ornatus.models.common import Formality
from ornatus.models.context import WeatherCondition
from ornatus.services.calendar_service import CalendarService
from ornatus.services.weather_service import WeatherService


def test_calendar_service_recognizes_client_dinner():
    occasion = CalendarService().get_occasion(
        "What should I wear to my client dinner Friday?", today=date(2026, 9, 2)
    )

    assert occasion.occasion == "client dinner"
    assert occasion.formality == Formality.BUSINESS_CASUAL
    assert occasion.start_time.weekday() == 4  # Friday
    assert occasion.start_time.date() >= date(2026, 9, 2)


def test_calendar_service_falls_back_to_generic_occasion():
    occasion = CalendarService().get_occasion("what's the plan?", today=date(2026, 9, 2))

    assert occasion.formality == Formality.CASUAL
    assert occasion.location is None


def test_weather_service_is_deterministic_for_a_given_date():
    service = WeatherService()

    first = service.get_weather("Downtown", date(2026, 9, 4))
    second = service.get_weather("Downtown", date(2026, 9, 4))

    assert first.model_dump(exclude={"generated_at"}) == second.model_dump(exclude={"generated_at"})
    assert first.condition in WeatherCondition
