import pytest

from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.services.outfit_service import UnknownWardrobeItemsError

USER_ID = "user-1"


def test_create_recommendation_persists_and_validates_item_ids(outfit_service, wardrobe_repository):
    wardrobe_repository.add(
        WardrobeItem(id="item-1", user_id=USER_ID, name="Navy Blazer", category=ItemCategory.OUTERWEAR)
    )

    recommendation = outfit_service.create_recommendation(
        USER_ID,
        request_text="client dinner Friday",
        item_ids=["item-1"],
        reasoning="Business casual dinner, cool evening.",
        event_reference="Client Dinner",
        weather_summary="clear, 52-68F",
        confidence=0.8,
    )

    assert recommendation.id
    assert recommendation.item_ids == ["item-1"]
    fetched = outfit_service.get(recommendation.id)
    assert fetched == recommendation


def test_create_recommendation_rejects_unknown_item_ids(outfit_service):
    with pytest.raises(UnknownWardrobeItemsError):
        outfit_service.create_recommendation(
            USER_ID,
            request_text="client dinner Friday",
            item_ids=["does-not-exist"],
            reasoning="n/a",
        )


def test_get_latest_for_user_returns_most_recent(outfit_service, wardrobe_repository):
    wardrobe_repository.add(WardrobeItem(id="item-1", user_id=USER_ID, name="A", category=ItemCategory.TOP))
    wardrobe_repository.add(WardrobeItem(id="item-2", user_id=USER_ID, name="B", category=ItemCategory.TOP))

    outfit_service.create_recommendation(USER_ID, "req 1", ["item-1"], "first")
    second = outfit_service.create_recommendation(USER_ID, "req 2", ["item-2"], "second")

    assert outfit_service.get_latest_for_user(USER_ID).id == second.id


def test_get_latest_for_user_returns_none_when_no_recommendations(outfit_service):
    assert outfit_service.get_latest_for_user("nobody") is None


def test_create_recommendation_persists_excluded_items_and_preferences_considered(
    outfit_service, wardrobe_repository
):
    wardrobe_repository.add(
        WardrobeItem(id="item-1", user_id=USER_ID, name="Oxford Shirt", category=ItemCategory.TOP)
    )
    wardrobe_repository.add(
        WardrobeItem(id="item-blazer", user_id=USER_ID, name="Navy Blazer", category=ItemCategory.OUTERWEAR)
    )

    recommendation = outfit_service.create_recommendation(
        USER_ID,
        request_text="client dinner Friday",
        item_ids=["item-1"],
        reasoning="Left out the blazer.",
        excluded_item_ids=["item-blazer"],
        preferences_considered=["pref-1"],
    )

    assert recommendation.excluded_item_ids == ["item-blazer"]
    assert recommendation.preferences_considered == ["pref-1"]
    assert outfit_service.get(recommendation.id).excluded_item_ids == ["item-blazer"]


def test_create_recommendation_rejects_unknown_excluded_item_ids(outfit_service, wardrobe_repository):
    wardrobe_repository.add(
        WardrobeItem(id="item-1", user_id=USER_ID, name="Oxford Shirt", category=ItemCategory.TOP)
    )

    with pytest.raises(UnknownWardrobeItemsError):
        outfit_service.create_recommendation(
            USER_ID,
            request_text="client dinner Friday",
            item_ids=["item-1"],
            reasoning="n/a",
            excluded_item_ids=["does-not-exist"],
        )
