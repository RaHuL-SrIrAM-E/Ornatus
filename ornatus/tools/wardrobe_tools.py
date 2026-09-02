"""Agent-facing tools over WardrobeService.

Tools stay thin: parse/validate input, delegate to the service, return
plain structured data. No business logic lives here.

Tools are built via a factory (rather than module-level ``@tool`` functions)
so they can be bound to a specific ``WardrobeService`` instance — this keeps
the orchestrator's wiring explicit and makes the tools testable in isolation.
"""

from strands import tool

from ornatus.models.wardrobe import ItemCategory, ItemStatus
from ornatus.services.wardrobe_service import WardrobeService


def make_wardrobe_tools(service: WardrobeService) -> list:
    @tool
    def get_wardrobe_items(
        user_id: str,
        category: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        """Look up items currently in a user's wardrobe.

        Args:
            user_id: The wardrobe owner's user id.
            category: Optional filter — one of "top", "bottom", "outerwear",
                "dress", "shoes", "accessory".
            status: Optional filter — one of "active", "laundry", "repair",
                "donated", "retired". Defaults to returning items of every
                status if omitted.

        Returns:
            A list of wardrobe items as structured dicts.
        """
        parsed_category = ItemCategory(category) if category else None
        parsed_status = ItemStatus(status) if status else None
        items = service.get_items(user_id, category=parsed_category, status=parsed_status)
        return [item.model_dump(mode="json") for item in items]

    return [get_wardrobe_items]
