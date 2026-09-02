from ornatus.models.feedback import PreferenceSignal
from ornatus.models.preferences import PreferenceType
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


def test_record_derives_item_level_preference_from_rejected_items(feedback_service, preference_service):
    feedback_service.record(
        USER_ID,
        feedback_text="I like that outfit, but I don't want to wear the blazer.",
        rejected_item_ids=["item-blazer-navy"],
    )

    preferences = preference_service.get_preferences(USER_ID)

    assert len(preferences) == 1
    assert preferences[0].type == PreferenceType.ITEM_DISLIKE
    assert preferences[0].value == "item-blazer-navy"
    assert preferences[0].reason == "I like that outfit, but I don't want to wear the blazer."


def test_record_with_no_rejected_items_creates_no_preference(feedback_service, preference_service):
    feedback_service.record(USER_ID, feedback_text="Looks great, thanks!")

    assert preference_service.get_preferences(USER_ID) == []


def test_record_persists_explicit_broader_preference_signals(feedback_service, preference_service):
    feedback_service.record(
        USER_ID,
        feedback_text="I don't like blazers for client dinners.",
        rejected_item_ids=["item-blazer-navy"],
        preference_signals=[
            {
                "type": "context_dislike",
                "value": "blazer",
                "context": "client dinner",
                "reason": "I don't like blazers for client dinners.",
            }
        ],
    )

    preferences = preference_service.get_preferences(USER_ID)
    by_type = {p.type: p for p in preferences}

    # Both the mechanical item-level signal and the explicit broader one exist.
    assert PreferenceType.ITEM_DISLIKE in by_type
    assert by_type[PreferenceType.ITEM_DISLIKE].value == "item-blazer-navy"
    assert PreferenceType.CONTEXT_DISLIKE in by_type
    assert by_type[PreferenceType.CONTEXT_DISLIKE].value == "blazer"
    assert by_type[PreferenceType.CONTEXT_DISLIKE].context == "client dinner"
