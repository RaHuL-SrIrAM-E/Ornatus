"""Agent-facing tool over OutfitService.

Recording a recommendation is a real, validated write (the service rejects
wardrobe item ids that don't exist) — not just text generation — which is
what makes this a genuine tool call rather than a formatting step.
"""

from strands import tool

from ornatus.services.outfit_service import OutfitService, UnknownWardrobeItemsError


def make_outfit_tools(service: OutfitService, user_id: str) -> list:
    @tool
    def record_outfit_recommendation(
        request_text: str,
        item_ids: list[str],
        reasoning: str,
        event_reference: str | None = None,
        weather_summary: str | None = None,
        confidence: float | None = None,
        excluded_item_ids: list[str] | None = None,
        preferences_considered: list[str] | None = None,
    ) -> dict:
        """Persist an outfit recommendation. Call this once you've decided on
        the wardrobe items to suggest, after checking context/weather/wardrobe
        (and, when relevant, learned preferences).

        Args:
            request_text: The user's original request.
            item_ids: The selected wardrobe item ids (must be real items
                returned by get_wardrobe_items/get_wardrobe_item).
            reasoning: A brief explanation of why this outfit fits the
                occasion and weather — and, if a learned preference changed
                the outcome, say so in plain language (e.g. "left out the
                navy blazer since you didn't want to wear it last time").
            event_reference: The occasion/event title this recommendation is
                for, if known.
            weather_summary: A short weather summary this recommendation
                accounted for, if known.
            confidence: Optional confidence score between 0 and 1.
            excluded_item_ids: Wardrobe item ids you deliberately left out
                because of a learned preference (from get_user_preferences),
                as opposed to items that just didn't fit the occasion/weather.
            preferences_considered: The ids of the preference signals (from
                get_user_preferences) that influenced this recommendation.

        Returns:
            The persisted recommendation as a structured dict, including its
            id.

        Raises:
            ValueError: If any item_id doesn't reference a real wardrobe item.
        """
        try:
            recommendation = service.create_recommendation(
                user_id,
                request_text=request_text,
                item_ids=item_ids,
                reasoning=reasoning,
                event_reference=event_reference,
                weather_summary=weather_summary,
                confidence=confidence,
                excluded_item_ids=excluded_item_ids,
                preferences_considered=preferences_considered,
            )
        except UnknownWardrobeItemsError as exc:
            raise ValueError(str(exc)) from exc
        return recommendation.model_dump(mode="json")

    return [record_outfit_recommendation]
