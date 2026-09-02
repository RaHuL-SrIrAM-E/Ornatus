from ornatus.models.feedback import PreferenceSignal
from ornatus.models.wardrobe import ItemCategory, WardrobeItem

USER_ID = "user-1"


def test_record_uses_explicit_recommendation_id(feedback_service):
    feedback = feedback_service.record(
        USER_ID,
        feedback_text="I don't want to wear the blazer.",
        recommendation_id="rec-explicit",
        rejected_item_ids=["item-blazer"],
        preference_signal=PreferenceSignal.MIXED,
    )

    assert feedback.recommendation_id == "rec-explicit"
    assert feedback.rejected_item_ids == ["item-blazer"]
    assert feedback.preference_signal == PreferenceSignal.MIXED


def test_record_defaults_to_latest_recommendation(feedback_service, outfit_service, wardrobe_repository):
    wardrobe_repository.add(
        WardrobeItem(id="item-1", user_id=USER_ID, name="Navy Blazer", category=ItemCategory.OUTERWEAR)
    )
    recommendation = outfit_service.create_recommendation(
        USER_ID, "client dinner Friday", ["item-1"], "reasoning"
    )

    feedback = feedback_service.record(USER_ID, feedback_text="I like it, but not the blazer.")

    assert feedback.recommendation_id == recommendation.id


def test_record_leaves_recommendation_id_none_when_no_recommendations_exist(feedback_service):
    feedback = feedback_service.record(USER_ID, feedback_text="general feedback")

    assert feedback.recommendation_id is None
