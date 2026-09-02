"""Deterministic occasion/calendar lookup.

Phase 1 has no real calendar integration. ``CalendarService.get_occasion``
is the seam a real calendar client plugs into later: same method signature,
same ``OccasionContext`` return type, no change needed in
``ornatus.tools.context_tools`` or the agent when that happens.

Matching is deliberately simple keyword lookup against a tiny seeded set —
not NLP — since Phase 1 only needs to demonstrate one real scenario
end-to-end ("client dinner Friday").
"""

from datetime import date, datetime, time, timedelta

from ornatus.models._util import new_id
from ornatus.models.common import Formality
from ornatus.models.context import OccasionContext


def _next_weekday(from_date: date, weekday: int) -> date:
    """Next date on/after `from_date` that falls on `weekday` (Mon=0..Sun=6)."""
    days_ahead = (weekday - from_date.weekday()) % 7
    return from_date + timedelta(days=days_ahead)


class CalendarService:
    def get_occasion(self, query: str, today: date | None = None) -> OccasionContext:
        today = today or date.today()
        lowered = query.lower()

        if "dinner" in lowered and "client" in lowered:
            dinner_date = _next_weekday(today, weekday=4)  # Friday
            return OccasionContext(
                id=new_id("occ"),
                title="Client Dinner",
                occasion="client dinner",
                start_time=datetime.combine(dinner_date, time(19, 0)),
                location="Downtown",
                formality=Formality.BUSINESS_CASUAL,
                notes="Reservation at 7pm; business clients attending.",
            )

        # No specific occasion recognized — a sensible, deterministic
        # default so the tool always returns something the agent can reason
        # about, rather than requiring special-case handling for "unknown".
        return OccasionContext(
            id=new_id("occ"),
            title="General Plans",
            occasion="everyday",
            start_time=datetime.combine(today, time(18, 0)),
            location=None,
            formality=Formality.CASUAL,
            notes=None,
        )
