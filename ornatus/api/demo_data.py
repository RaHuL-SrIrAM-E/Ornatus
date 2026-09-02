"""Sample wardrobe data for the Phase 1 milestone demo.

Not a fixture for tests (see tests/conftest.py for that) — just enough
inventory, spanning both business-casual and casual pieces, for the agent
to have a real choice to reason over for the "client dinner Friday" scenario
and others like it.
"""

from ornatus.config.settings import get_settings
from ornatus.models.common import Formality, Season
from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.services.wardrobe_service import WardrobeService

DEMO_USER_ID = get_settings().current_user_id

_SAMPLE_ITEMS = [
    WardrobeItem(
        id="item-blazer-navy",
        user_id=DEMO_USER_ID,
        name="Navy Blazer",
        category=ItemCategory.OUTERWEAR,
        subcategory="blazer",
        colors=["navy"],
        material="wool",
        brand="Suitsupply",
        formality=Formality.BUSINESS_CASUAL,
        season=[Season.FALL, Season.WINTER, Season.SPRING],
        suitable_occasions=["work", "client dinner", "networking"],
        style_tags=["classic", "tailored"],
    ),
    WardrobeItem(
        id="item-shirt-oxford-white",
        user_id=DEMO_USER_ID,
        name="White Oxford Shirt",
        category=ItemCategory.TOP,
        subcategory="dress shirt",
        colors=["white"],
        material="cotton",
        brand="Everlane",
        formality=Formality.BUSINESS_CASUAL,
        season=[Season.ALL_SEASON],
        suitable_occasions=["work", "client dinner"],
        style_tags=["classic"],
    ),
    WardrobeItem(
        id="item-shirt-light-blue",
        user_id=DEMO_USER_ID,
        name="Light Blue Shirt",
        category=ItemCategory.TOP,
        subcategory="dress shirt",
        colors=["light blue"],
        material="cotton",
        brand="Uniqlo",
        formality=Formality.SMART_CASUAL,
        season=[Season.ALL_SEASON],
        suitable_occasions=["work", "brunch"],
        style_tags=["classic"],
    ),
    WardrobeItem(
        id="item-trousers-charcoal",
        user_id=DEMO_USER_ID,
        name="Charcoal Trousers",
        category=ItemCategory.BOTTOM,
        subcategory="dress trousers",
        colors=["charcoal"],
        material="wool blend",
        brand="J.Crew",
        formality=Formality.BUSINESS_CASUAL,
        season=[Season.FALL, Season.WINTER, Season.SPRING],
        suitable_occasions=["work", "client dinner"],
        style_tags=["tailored"],
    ),
    WardrobeItem(
        id="item-jeans-dark-denim",
        user_id=DEMO_USER_ID,
        name="Dark Denim Jeans",
        category=ItemCategory.BOTTOM,
        subcategory="jeans",
        colors=["indigo"],
        material="denim",
        brand="Levi's",
        formality=Formality.CASUAL,
        season=[Season.ALL_SEASON],
        suitable_occasions=["weekend", "casual outings"],
        style_tags=["everyday"],
    ),
    WardrobeItem(
        id="item-chinos-beige",
        user_id=DEMO_USER_ID,
        name="Beige Chinos",
        category=ItemCategory.BOTTOM,
        subcategory="chinos",
        colors=["beige"],
        material="cotton twill",
        brand="J.Crew",
        formality=Formality.SMART_CASUAL,
        season=[Season.SPRING, Season.SUMMER, Season.FALL],
        suitable_occasions=["work", "brunch", "dates"],
        style_tags=["smart-casual"],
    ),
    WardrobeItem(
        id="item-sneakers-white",
        user_id=DEMO_USER_ID,
        name="White Sneakers",
        category=ItemCategory.SHOES,
        subcategory="sneakers",
        colors=["white"],
        material="leather",
        brand="Adidas",
        formality=Formality.CASUAL,
        season=[Season.ALL_SEASON],
        suitable_occasions=["weekend", "casual outings"],
        style_tags=["everyday"],
    ),
    WardrobeItem(
        id="item-loafers-brown",
        user_id=DEMO_USER_ID,
        name="Brown Loafers",
        category=ItemCategory.SHOES,
        subcategory="loafers",
        colors=["brown"],
        material="leather",
        brand="Allen Edmonds",
        formality=Formality.BUSINESS_CASUAL,
        season=[Season.ALL_SEASON],
        suitable_occasions=["work", "client dinner", "dates"],
        style_tags=["classic"],
    ),
]


def seed_demo_wardrobe(service: WardrobeService) -> None:
    if service.get_items(DEMO_USER_ID):
        return
    for item in _SAMPLE_ITEMS:
        service.add_item(item)
