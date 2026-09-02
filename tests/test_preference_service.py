from ornatus.models.preferences import PreferenceType

USER_ID = "user-1"


def test_record_persists_and_returns_preference(preference_service):
    preference = preference_service.record(
        USER_ID,
        preference_type=PreferenceType.ITEM_DISLIKE,
        value="item-blazer-navy",
        reason="I don't want to wear the blazer.",
    )

    assert preference.id
    assert preference.type == PreferenceType.ITEM_DISLIKE
    assert preference.value == "item-blazer-navy"
    assert preference.confidence == 1.0


def test_get_preferences_returns_recorded_signals(preference_service):
    preference_service.record(USER_ID, PreferenceType.ITEM_DISLIKE, "item-blazer-navy")

    preferences = preference_service.get_preferences(USER_ID)

    assert [p.value for p in preferences] == ["item-blazer-navy"]


def test_get_preferences_scopes_by_context(preference_service):
    preference_service.record(
        USER_ID, PreferenceType.CONTEXT_DISLIKE, "blazer", context="dinner"
    )
    preference_service.record(
        USER_ID, PreferenceType.CONTEXT_DISLIKE, "sneakers", context="work"
    )

    dinner_preferences = preference_service.get_preferences(USER_ID, context="client dinner")

    assert [p.value for p in dinner_preferences] == ["blazer"]
