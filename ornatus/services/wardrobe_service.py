"""Deterministic wardrobe logic — no LLM involved.

This is the layer wardrobe_tools.py calls into. It exists separately from
the repository so business rules (filtering, future gap-analysis, etc.) have
somewhere to live that isn't SQL and isn't agent-facing tool plumbing.
"""

from ornatus.models.wardrobe import ItemCategory, ItemStatus, WardrobeItem
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository


class WardrobeService:
    def __init__(self, repository: WardrobeRepository):
        self._repository = repository

    def get_items(
        self,
        user_id: str,
        category: ItemCategory | None = None,
        status: ItemStatus | None = None,
    ) -> list[WardrobeItem]:
        return self._repository.list_for_user(user_id, category=category, status=status)

    def add_item(self, item: WardrobeItem) -> WardrobeItem:
        return self._repository.add(item)
