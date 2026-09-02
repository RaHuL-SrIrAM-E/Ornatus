from datetime import date

from ornatus.models.wardrobe import ItemCategory, WardrobeItem


def _item(item_id: str, **overrides) -> WardrobeItem:
    defaults = dict(id=item_id, user_id="user-1", name=item_id, category=ItemCategory.SHOES)
    defaults.update(overrides)
    return WardrobeItem(**defaults)


def test_add_item_then_get_items(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))

    items = wardrobe_service.get_items("user-1")

    assert [i.id for i in items] == ["item-1"]


def test_get_items_empty_for_unknown_user(wardrobe_service):
    assert wardrobe_service.get_items("nobody") == []


def test_get_item_returns_none_when_missing(wardrobe_service):
    assert wardrobe_service.get_item("nope") is None


def test_get_item_returns_added_item(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))

    assert wardrobe_service.get_item("item-1").id == "item-1"


def test_update_item_persists(wardrobe_service):
    item = _item("item-1")
    wardrobe_service.add_item(item)

    item.name = "Renamed"
    wardrobe_service.update_item(item)

    assert wardrobe_service.get_item("item-1").name == "Renamed"


def test_mark_worn_updates_wear_count(wardrobe_service):
    wardrobe_service.add_item(_item("item-1"))

    updated = wardrobe_service.mark_worn("item-1", worn_on=date(2026, 9, 4))

    assert updated.wear_count == 1
    assert updated.last_worn_date == date(2026, 9, 4)
