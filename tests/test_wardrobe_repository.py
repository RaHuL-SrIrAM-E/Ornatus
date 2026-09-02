from ornatus.models.wardrobe import ItemCategory, ItemStatus, WardrobeItem


def make_item(item_id: str, category: ItemCategory = ItemCategory.TOP, **overrides) -> WardrobeItem:
    defaults = dict(id=item_id, user_id="user-1", category=category, colors=["blue"], tags=["casual"])
    defaults.update(overrides)
    return WardrobeItem(**defaults)


def test_add_and_get_round_trips(wardrobe_repository):
    item = make_item("item-1")

    wardrobe_repository.add(item)
    fetched = wardrobe_repository.get("item-1")

    assert fetched is not None
    assert fetched.id == "item-1"
    assert fetched.colors == ["blue"]
    assert fetched.tags == ["casual"]


def test_get_missing_returns_none(wardrobe_repository):
    assert wardrobe_repository.get("does-not-exist") is None


def test_list_for_user_filters_by_category_and_status(wardrobe_repository):
    wardrobe_repository.add(make_item("item-1", category=ItemCategory.TOP))
    wardrobe_repository.add(make_item("item-2", category=ItemCategory.BOTTOM))
    wardrobe_repository.add(
        make_item("item-3", category=ItemCategory.TOP, status=ItemStatus.LAUNDRY)
    )

    all_items = wardrobe_repository.list_for_user("user-1")
    tops = wardrobe_repository.list_for_user("user-1", category=ItemCategory.TOP)
    active_tops = wardrobe_repository.list_for_user(
        "user-1", category=ItemCategory.TOP, status=ItemStatus.ACTIVE
    )

    assert {i.id for i in all_items} == {"item-1", "item-2", "item-3"}
    assert {i.id for i in tops} == {"item-1", "item-3"}
    assert {i.id for i in active_tops} == {"item-1"}


def test_list_for_user_scopes_by_user(wardrobe_repository):
    wardrobe_repository.add(make_item("item-1"))
    wardrobe_repository.add(make_item("item-2", user_id="user-2"))

    assert [i.id for i in wardrobe_repository.list_for_user("user-1")] == ["item-1"]
