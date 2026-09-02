from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.tools.wardrobe_tools import make_wardrobe_tools


def test_get_wardrobe_items_tool_returns_structured_data(wardrobe_service):
    wardrobe_service.add_item(WardrobeItem(id="item-1", user_id="user-1", category=ItemCategory.TOP))
    (get_wardrobe_items,) = make_wardrobe_tools(wardrobe_service)

    result = get_wardrobe_items(user_id="user-1")

    assert isinstance(result, list)
    assert result[0]["id"] == "item-1"
    assert result[0]["category"] == "top"


def test_get_wardrobe_items_tool_applies_category_filter(wardrobe_service):
    wardrobe_service.add_item(WardrobeItem(id="item-1", user_id="user-1", category=ItemCategory.TOP))
    wardrobe_service.add_item(WardrobeItem(id="item-2", user_id="user-1", category=ItemCategory.SHOES))
    (get_wardrobe_items,) = make_wardrobe_tools(wardrobe_service)

    result = get_wardrobe_items(user_id="user-1", category="shoes")

    assert [item["id"] for item in result] == ["item-2"]
