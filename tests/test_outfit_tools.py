import pytest

from ornatus.models.wardrobe import ItemCategory, WardrobeItem
from ornatus.tools.outfit_tools import make_outfit_tools

USER_ID = "user-1"


def test_record_outfit_recommendation_tool_persists(outfit_service, wardrobe_repository):
    wardrobe_repository.add(
        WardrobeItem(id="item-1", user_id=USER_ID, name="Navy Blazer", category=ItemCategory.OUTERWEAR)
    )
    (record_outfit_recommendation,) = make_outfit_tools(outfit_service, USER_ID)

    result = record_outfit_recommendation(
        request_text="client dinner Friday",
        item_ids=["item-1"],
        reasoning="Business casual dinner.",
    )

    assert result["item_ids"] == ["item-1"]
    assert outfit_service.get(result["id"]) is not None


def test_record_outfit_recommendation_tool_rejects_unknown_items(outfit_service):
    (record_outfit_recommendation,) = make_outfit_tools(outfit_service, USER_ID)

    with pytest.raises(ValueError):
        record_outfit_recommendation(
            request_text="client dinner Friday",
            item_ids=["does-not-exist"],
            reasoning="n/a",
        )
