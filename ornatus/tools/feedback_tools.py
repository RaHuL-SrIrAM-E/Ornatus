"""Agent-facing tool over FeedbackService."""

from strands import tool

from ornatus.models.feedback import PreferenceSignal
from ornatus.services.feedback_service import FeedbackService


def make_feedback_tools(service: FeedbackService, user_id: str) -> list:
    @tool
    def record_feedback(
        feedback_text: str,
        recommendation_id: str | None = None,
        rejected_item_ids: list[str] | None = None,
        preference_signal: str = "neutral",
    ) -> dict:
        """Record the user's feedback on an outfit recommendation.

        Args:
            feedback_text: The user's feedback, close to verbatim.
            recommendation_id: The recommendation this feedback is about, if
                known. If omitted, this is recorded against the user's most
                recent recommendation.
            rejected_item_ids: Wardrobe item ids the user pushed back on, if
                you were able to identify them (e.g. by looking them up with
                get_wardrobe_items first).
            preference_signal: The overall sentiment — one of "positive",
                "negative", "mixed", "neutral".

        Returns:
            The persisted feedback as a structured dict, including its id.
        """
        feedback = service.record(
            user_id,
            feedback_text=feedback_text,
            recommendation_id=recommendation_id,
            rejected_item_ids=rejected_item_ids,
            preference_signal=PreferenceSignal(preference_signal),
        )
        return feedback.model_dump(mode="json")

    return [record_feedback]
