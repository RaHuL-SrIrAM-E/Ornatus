"""Persists user feedback on a recommendation.

Phase 1's "memory/preferences abstraction": this only records the signal.
Folding it into ``ornatus.models.preferences.Preferences`` (learned weights)
is intentionally deferred — see the project README.
"""

from ornatus.models._util import new_id
from ornatus.models.feedback import Feedback, PreferenceSignal
from ornatus.persistence.repositories.feedback_repository import FeedbackRepository
from ornatus.services.outfit_service import OutfitService


class FeedbackService:
    def __init__(self, repository: FeedbackRepository, outfit_service: OutfitService):
        self._repository = repository
        self._outfit_service = outfit_service

    def record(
        self,
        user_id: str,
        feedback_text: str,
        recommendation_id: str | None = None,
        rejected_item_ids: list[str] | None = None,
        preference_signal: PreferenceSignal = PreferenceSignal.NEUTRAL,
    ) -> Feedback:
        if recommendation_id is None:
            latest = self._outfit_service.get_latest_for_user(user_id)
            recommendation_id = latest.id if latest else None

        feedback = Feedback(
            id=new_id("fb"),
            user_id=user_id,
            recommendation_id=recommendation_id,
            feedback_text=feedback_text,
            rejected_item_ids=rejected_item_ids or [],
            preference_signal=preference_signal,
        )
        return self._repository.add(feedback)

    def list_for_user(self, user_id: str) -> list[Feedback]:
        return self._repository.list_for_user(user_id)
