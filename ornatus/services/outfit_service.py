"""Deterministic outfit-recommendation logic — no LLM involved.

The agent reasons about *which* items to pick; this service only validates
and persists that decision. Validation matters here specifically: an
``OutfitRecommendation`` must reference real wardrobe items, so a
recommendation citing an id that doesn't exist is rejected rather than
silently stored.
"""

from ornatus.models._util import new_id
from ornatus.models.outfit import OutfitRecommendation
from ornatus.persistence.repositories.outfit_recommendation_repository import (
    OutfitRecommendationRepository,
)
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository


class UnknownWardrobeItemsError(ValueError):
    def __init__(self, item_ids: list[str]):
        self.item_ids = item_ids
        super().__init__(f"Unknown wardrobe item id(s): {', '.join(item_ids)}")


class OutfitService:
    def __init__(
        self,
        recommendation_repository: OutfitRecommendationRepository,
        wardrobe_repository: WardrobeRepository,
    ):
        self._recommendations = recommendation_repository
        self._wardrobe = wardrobe_repository

    def create_recommendation(
        self,
        user_id: str,
        request_text: str,
        item_ids: list[str],
        reasoning: str,
        event_reference: str | None = None,
        weather_summary: str | None = None,
        confidence: float | None = None,
        excluded_item_ids: list[str] | None = None,
        preferences_considered: list[str] | None = None,
    ) -> OutfitRecommendation:
        excluded_item_ids = excluded_item_ids or []
        missing = [
            item_id
            for item_id in [*item_ids, *excluded_item_ids]
            if self._wardrobe.get(item_id) is None
        ]
        if missing:
            raise UnknownWardrobeItemsError(missing)

        recommendation = OutfitRecommendation(
            id=new_id("rec"),
            user_id=user_id,
            request_text=request_text,
            item_ids=item_ids,
            reasoning=reasoning,
            event_reference=event_reference,
            weather_summary=weather_summary,
            confidence=confidence,
            excluded_item_ids=excluded_item_ids,
            preferences_considered=preferences_considered or [],
        )
        return self._recommendations.add(recommendation)

    def get(self, recommendation_id: str) -> OutfitRecommendation | None:
        return self._recommendations.get(recommendation_id)

    def get_latest_for_user(self, user_id: str) -> OutfitRecommendation | None:
        return self._recommendations.get_latest_for_user(user_id)
