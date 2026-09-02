from ornatus.models.preferences import PreferenceType
from ornatus.tools.preference_tools import make_preference_tools

USER_ID = "user-1"


def test_get_user_preferences_tool_returns_structured_signals(preference_service):
    preference_service.record(USER_ID, PreferenceType.ITEM_DISLIKE, "item-blazer-navy", reason="feedback")
    (get_user_preferences,) = make_preference_tools(preference_service, USER_ID)

    result = get_user_preferences()

    assert len(result) == 1
    assert result[0]["type"] == "item_dislike"
    assert result[0]["value"] == "item-blazer-navy"


def test_get_user_preferences_tool_applies_context(preference_service):
    preference_service.record(USER_ID, PreferenceType.CONTEXT_DISLIKE, "blazer", context="dinner")
    preference_service.record(USER_ID, PreferenceType.CONTEXT_DISLIKE, "sneakers", context="work")
    (get_user_preferences,) = make_preference_tools(preference_service, USER_ID)

    result = get_user_preferences(context="client dinner")

    assert [p["value"] for p in result] == ["blazer"]
