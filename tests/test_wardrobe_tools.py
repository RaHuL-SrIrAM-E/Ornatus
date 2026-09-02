from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.tools.wardrobe_tools import make_wardrobe_tools

USER_ID = "user-1"


def _item(item_id: str, **overrides) -> WardrobeItem:
    defaults = dict(id=item_id, user_id=USER_ID, name=item_id, category=ItemCategory.TOP)
    defaults.update(overrides)
    return WardrobeItem(**defaults)


def test_get_wardrobe_items_tool_returns_structured_data(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))
    get_wardrobe_items, _, _ = make_wardrobe_tools(wardrobe_service, USER_ID)

    result = get_wardrobe_items()

    assert isinstance(result, list)
    assert result[0]["id"] == "item-1"
    assert result[0]["category"] == "top"


def test_get_wardrobe_items_tool_applies_category_filter(wardrobe_service):
    wardrobe_service.add_item(_item("item-1", category=ItemCategory.TOP))
    wardrobe_service.add_item(_item("item-2", category=ItemCategory.SHOES))
    get_wardrobe_items, _, _ = make_wardrobe_tools(wardrobe_service, USER_ID)

    result = get_wardrobe_items(category="shoes")

    assert [item["id"] for item in result] == ["item-2"]


def test_get_wardrobe_items_tool_only_returns_current_users_items(wardrobe_service):
    wardrobe_service.add_item(_item("item-1", user_id=USER_ID))
    wardrobe_service.add_item(_item("item-2", user_id="someone-else"))
    get_wardrobe_items, _, _ = make_wardrobe_tools(wardrobe_service, USER_ID)

    result = get_wardrobe_items()

    assert [item["id"] for item in result] == ["item-1"]


def test_get_wardrobe_item_tool_returns_single_item(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))
    _, get_wardrobe_item, _ = make_wardrobe_tools(wardrobe_service, USER_ID)

    assert get_wardrobe_item(item_id="item-1")["id"] == "item-1"
    assert get_wardrobe_item(item_id="missing") is None


def test_mark_wardrobe_item_worn_tool_updates_wear_count(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))
    _, _, mark_wardrobe_item_worn = make_wardrobe_tools(wardrobe_service, USER_ID)

    result = mark_wardrobe_item_worn(item_id="item-1")

    assert result["wear_count"] == 1
    assert result["last_worn_date"] is not None
