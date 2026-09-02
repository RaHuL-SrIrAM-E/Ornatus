"""Deterministic preference-signal logic — no LLM involved.

Persists and retrieves ``LearnedPreference`` rows. It doesn't derive
meaning from raw feedback text (that's the agent's job, or the mechanical
item-id conversion in ``FeedbackService``) — it only validates the
structured type/value/context it's given and stores it.
"""

from ornatus.models._util import new_id, utc_now
from ornatus.models.preferences import LearnedPreference, PreferenceType
from ornatus.persistence.repositories.preference_repository import PreferenceRepository


class PreferenceService:
    def __init__(self, repository: PreferenceRepository):
        self._repository = repository

    def record(
        self,
        user_id: str,
        preference_type: PreferenceType,
        value: str,
        context: str | None = None,
        reason: str | None = None,
        source: str = "feedback",
        confidence: float = 1.0,
    ) -> LearnedPreference:
        now = utc_now()
        preference = LearnedPreference(
            id=new_id("pref"),
            user_id=user_id,
            type=preference_type,
            value=value,
            context=context,
            reason=reason,
            source=source,
            confidence=confidence,
            created_at=now,
            updated_at=now,
        )
        return self._repository.add(preference)

    def get_preferences(self, user_id: str, context: str | None = None) -> list[LearnedPreference]:
        return self._repository.list_for_user(user_id, context=context)
