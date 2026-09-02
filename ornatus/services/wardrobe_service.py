"""Deterministic wardrobe logic — no LLM involved.

This is the layer wardrobe_tools.py calls into. It exists separately from
the repository so business rules (filtering, "mark worn", future
gap-analysis, etc.) have somewhere to live that isn't SQL and isn't
agent-facing tool plumbing.
"""

from datetime import date

from ornatus.models.common import Formality, Season
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
        formality: Formality | None = None,
        season: Season | None = None,
        occasion: str | None = None,
    ) -> list[WardrobeItem]:
        return self._repository.list_for_user(
            user_id,
            category=category,
            status=status,
            formality=formality,
            season=season,
            occasion=occasion,
        )

    def get_item(self, item_id: str) -> WardrobeItem | None:
        return self._repository.get(item_id)

    def add_item(self, item: WardrobeItem) -> WardrobeItem:
        return self._repository.add(item)

    def update_item(self, item: WardrobeItem) -> WardrobeItem:
        return self._repository.update(item)

    def mark_worn(self, item_id: str, worn_on: date | None = None) -> WardrobeItem | None:
        return self._repository.mark_worn(item_id, worn_on or date.today())
