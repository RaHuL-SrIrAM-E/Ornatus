from ornatus.models.wardrobe import ItemCategory, WardrobeItem


def test_add_item_then_get_items(wardrobe_service):
    item = WardrobeItem(id="item-1", user_id="user-1", category=ItemCategory.SHOES)

    wardrobe_service.add_item(item)
    items = wardrobe_service.get_items("user-1")

    assert [i.id for i in items] == ["item-1"]


def test_get_items_empty_for_unknown_user(wardrobe_service):
    assert wardrobe_service.get_items("nobody") == []
