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
        preference_signals: list[dict] | None = None,
    ) -> dict:
        """Record the user's feedback on an outfit recommendation. Every id in
        rejected_item_ids automatically becomes a remembered item-level
        dislike — no need to also pass it in preference_signals.

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
            preference_signals: Broader preferences to remember, only when
                the feedback text actually supports something wider than
                "don't use this one item" — e.g. the user said they dislike
                a whole category, or a category for a specific occasion.
                Each entry: {"type": one of "item_dislike"/"item_like"/
                "category_dislike"/"category_like"/"context_dislike"/
                "context_like"/"general", "value": what it's about (a
                category/subcategory string, or a free descriptor for
                "general"), "context": the occasion, only for the
                context_* types (e.g. "client dinner"), "reason": optional
                short rationale}. Leave empty rather than guess — a single
                rejected item should usually stay item-level only.

        Returns:
            The persisted feedback as a structured dict, including its id.
        """
        feedback = service.record(
            user_id,
            feedback_text=feedback_text,
            recommendation_id=recommendation_id,
            rejected_item_ids=rejected_item_ids,
            preference_signal=PreferenceSignal(preference_signal),
            preference_signals=preference_signals,
        )
        return feedback.model_dump(mode="json")

    return [record_feedback]
