"""Sample wardrobe data for the Phase 1 milestone demo.

Not a fixture for tests (see tests/conftest.py for that) — just enough
inventory for the CLI to have something real to reason over.
"""

from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.services.wardrobe_service import WardrobeService

DEMO_USER_ID = "demo-user"

_SAMPLE_ITEMS = [
    WardrobeItem(
        id="item-1",
        user_id=DEMO_USER_ID,
        category=ItemCategory.OUTERWEAR,
        subcategory="raincoat",
        colors=["navy"],
        brand="Uniqlo",
        tags=["waterproof", "packable"],
    ),
    WardrobeItem(
        id="item-2",
        user_id=DEMO_USER_ID,
        category=ItemCategory.TOP,
        subcategory="oxford shirt",
        colors=["white"],
        brand="Everlane",
        tags=["smart-casual"],
    ),
    WardrobeItem(
        id="item-3",
        user_id=DEMO_USER_ID,
        category=ItemCategory.BOTTOM,
        subcategory="chinos",
        colors=["olive"],
        brand="J.Crew",
        tags=["smart-casual"],
    ),
    WardrobeItem(
        id="item-4",
        user_id=DEMO_USER_ID,
        category=ItemCategory.SHOES,
        subcategory="sneakers",
        colors=["white"],
        brand="Adidas",
        tags=["casual"],
    ),
]


def seed_demo_wardrobe(service: WardrobeService) -> None:
    if service.get_items(DEMO_USER_ID):
        return
    for item in _SAMPLE_ITEMS:
        service.add_item(item)
