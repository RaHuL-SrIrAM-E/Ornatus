"""Agent-facing tools over WardrobeService.

Tools stay thin: parse/validate input, delegate to the service, return
plain structured data. No business logic lives here.

Tools are built via a factory (rather than module-level ``@tool`` functions)
so they can be bound to a specific ``WardrobeService`` instance and to the
current user — Phase 1 is single-user, so tools bind ``user_id`` internally
rather than asking the model to supply it (one less thing for the model to
get wrong, and there's no multi-tenancy to route on yet).
"""

from strands import tool

from ornatus.models.common import Formality, Season
from ornatus.models.wardrobe import ItemCategory, ItemStatus
from ornatus.services.wardrobe_service import WardrobeService


def make_wardrobe_tools(service: WardrobeService, user_id: str) -> list:
    @tool
    def get_wardrobe_items(
        category: str | None = None,
        status: str | None = None,
        formality: str | None = None,
        season: str | None = None,
        occasion: str | None = None,
    ) -> list[dict]:
        """List/search the user's wardrobe items, optionally filtered.

        Args:
            category: Optional filter — one of "top", "bottom", "outerwear",
                "dress", "shoes", "accessory".
            status: Optional filter — one of "active", "laundry", "repair",
                "donated", "retired". Defaults to every status if omitted.
            formality: Optional filter — one of "casual", "smart_casual",
                "business_casual", "formal".
            season: Optional filter — one of "spring", "summer", "fall",
                "winter", "all_season".
            occasion: Optional free-text filter matched against each item's
                suitable occasions (e.g. "client dinner", "work").

        Returns:
            A list of matching wardrobe items as structured dicts.
        """
        items = service.get_items(
            user_id,
            category=ItemCategory(category) if category else None,
            status=ItemStatus(status) if status else None,
            formality=Formality(formality) if formality else None,
            season=Season(season) if season else None,
            occasion=occasion,
        )
        return [item.model_dump(mode="json") for item in items]

    @tool
    def get_wardrobe_item(item_id: str) -> dict | None:
        """Retrieve a single wardrobe item by id.

        Args:
            item_id: The wardrobe item's id.

        Returns:
            The item as a structured dict, or null if no such item exists.
        """
        item = service.get_item(item_id)
        return item.model_dump(mode="json") if item else None

    @tool
    def mark_wardrobe_item_worn(item_id: str) -> dict | None:
        """Mark a wardrobe item as worn today: increments its wear count and
        sets its last-worn date to today.

        Args:
            item_id: The wardrobe item's id.

        Returns:
            The updated item as a structured dict, or null if no such item
            exists.
        """
        item = service.mark_worn(item_id)
        return item.model_dump(mode="json") if item else None

    return [get_wardrobe_items, get_wardrobe_item, mark_wardrobe_item_worn]
