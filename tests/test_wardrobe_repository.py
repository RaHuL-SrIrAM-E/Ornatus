from ornatus.models.common import Formality, Season
from ornatus.models.wardrobe import ItemCategory, ItemStatus, WardrobeItem


def make_item(item_id: str, category: ItemCategory = ItemCategory.TOP, **overrides) -> WardrobeItem:
    defaults = dict(
        id=item_id,
        user_id="user-1",
        name=f"Item {item_id}",
        category=category,
        colors=["blue"],
        style_tags=["casual"],
    )
    defaults.update(overrides)
    return WardrobeItem(**defaults)


def test_add_and_get_round_trips(wardrobe_repository):
    item = make_item("item-1")

    wardrobe_repository.add(item)
    fetched = wardrobe_repository.get("item-1")

    assert fetched is not None
    assert fetched.id == "item-1"
    assert fetched.name == "Item item-1"
    assert fetched.colors == ["blue"]
    assert fetched.style_tags == ["casual"]
    assert fetched.season == [Season.ALL_SEASON]


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


def test_list_for_user_filters_by_formality_season_and_occasion(wardrobe_repository):
    wardrobe_repository.add(
        make_item(
            "item-blazer",
            category=ItemCategory.OUTERWEAR,
            formality=Formality.BUSINESS_CASUAL,
            season=[Season.FALL, Season.WINTER],
            suitable_occasions=["client dinner", "work"],
        )
    )
    wardrobe_repository.add(
        make_item(
            "item-tee",
            category=ItemCategory.TOP,
            formality=Formality.CASUAL,
            season=[Season.SUMMER],
            suitable_occasions=["weekend"],
        )
    )

    business_casual = wardrobe_repository.list_for_user("user-1", formality=Formality.BUSINESS_CASUAL)
    winter_items = wardrobe_repository.list_for_user("user-1", season=Season.WINTER)
    dinner_items = wardrobe_repository.list_for_user("user-1", occasion="client dinner")

    assert [i.id for i in business_casual] == ["item-blazer"]
    assert [i.id for i in winter_items] == ["item-blazer"]
    assert [i.id for i in dinner_items] == ["item-blazer"]


def test_list_for_user_scopes_by_user(wardrobe_repository):
    wardrobe_repository.add(make_item("item-1"))
    wardrobe_repository.add(make_item("item-2", user_id="user-2"))

    assert [i.id for i in wardrobe_repository.list_for_user("user-1")] == ["item-1"]


def test_update_persists_changes(wardrobe_repository):
    item = make_item("item-1", status=ItemStatus.ACTIVE)
    wardrobe_repository.add(item)

    item.status = ItemStatus.LAUNDRY
    wardrobe_repository.update(item)

    assert wardrobe_repository.get("item-1").status == ItemStatus.LAUNDRY


def test_mark_worn_increments_wear_count_and_sets_last_worn_date(wardrobe_repository):
    from datetime import date

    wardrobe_repository.add(make_item("item-1"))

    updated = wardrobe_repository.mark_worn("item-1", worn_on=date(2026, 9, 4))

    assert updated.wear_count == 1
    assert updated.last_worn_date == date(2026, 9, 4)

    updated_again = wardrobe_repository.mark_worn("item-1", worn_on=date(2026, 9, 5))
    assert updated_again.wear_count == 2


def test_mark_worn_missing_item_returns_none(wardrobe_repository):
    from datetime import date

    assert wardrobe_repository.mark_worn("does-not-exist", worn_on=date.today()) is None
