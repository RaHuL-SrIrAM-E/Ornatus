"""Persists user feedback on a recommendation, and converts it into
``LearnedPreference`` signals — the seam that closes the feedback loop.

Two ways a signal gets created here, and only two — nothing in this service
guesses at meaning beyond them:

1. Mechanically: every id in ``rejected_item_ids`` becomes an item-level
   dislike. This needs no interpretation — a rejected item id is already a
   structured fact.
2. Explicitly: the caller (the agent, reasoning over the feedback text) can
   pass ``preference_signals`` — already-typed, already-scoped signals
   (category/context/general) it has judged the feedback actually supports.
   This service validates and persists them; it does not itself infer a
   broader signal from raw text, which would mean guessing at meaning this
   service has no way to verify.
"""

from ornatus.models._util import new_id
from ornatus.models.feedback import Feedback, PreferenceSignal
from ornatus.models.preferences import PreferenceType
from ornatus.persistence.repositories.feedback_repository import FeedbackRepository
from ornatus.services.outfit_service import OutfitService
from ornatus.services.preference_service import PreferenceService


class FeedbackService:
    def __init__(
        self,
        repository: FeedbackRepository,
        outfit_service: OutfitService,
        preference_service: PreferenceService,
    ):
        self._repository = repository
        self._outfit_service = outfit_service
        self._preference_service = preference_service

    def record(
        self,
        user_id: str,
        feedback_text: str,
        recommendation_id: str | None = None,
        rejected_item_ids: list[str] | None = None,
        preference_signal: PreferenceSignal = PreferenceSignal.NEUTRAL,
        preference_signals: list[dict] | None = None,
    ) -> Feedback:
        if recommendation_id is None:
            latest = self._outfit_service.get_latest_for_user(user_id)
            recommendation_id = latest.id if latest else None

        rejected_item_ids = rejected_item_ids or []
        feedback = Feedback(
            id=new_id("fb"),
            user_id=user_id,
            recommendation_id=recommendation_id,
            feedback_text=feedback_text,
            rejected_item_ids=rejected_item_ids,
            preference_signal=preference_signal,
        )
        self._repository.add(feedback)

        for item_id in rejected_item_ids:
            self._preference_service.record(
                user_id,
                preference_type=PreferenceType.ITEM_DISLIKE,
                value=item_id,
                reason=feedback_text,
                source="feedback",
            )

        for signal in preference_signals or []:
            self._preference_service.record(
                user_id,
                preference_type=PreferenceType(signal["type"]),
                value=signal["value"],
                context=signal.get("context"),
                reason=signal.get("reason", feedback_text),
                source="feedback",
                confidence=signal.get("confidence", 1.0),
            )

        return feedback

    def list_for_user(self, user_id: str) -> list[Feedback]:
        return self._repository.list_for_user(user_id)
