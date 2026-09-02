from ornatus.models.preferences import LearnedPreference, PreferenceType

USER_ID = "user-1"


def _pref(pref_id: str, **overrides) -> LearnedPreference:
    defaults = dict(
        id=pref_id,
        user_id=USER_ID,
        type=PreferenceType.ITEM_DISLIKE,
        value="item-blazer-navy",
    )
    defaults.update(overrides)
    return LearnedPreference(**defaults)


def test_add_and_get_round_trips(preference_repository):
    preference_repository.add(_pref("pref-1", reason="didn't want to wear it"))

    fetched = preference_repository.get("pref-1")

    assert fetched is not None
    assert fetched.value == "item-blazer-navy"
    assert fetched.reason == "didn't want to wear it"
    assert fetched.active is True


def test_list_for_user_returns_only_that_users_preferences(preference_repository):
    preference_repository.add(_pref("pref-1"))
    preference_repository.add(_pref("pref-2", user_id="user-2"))

    assert [p.id for p in preference_repository.list_for_user(USER_ID)] == ["pref-1"]


def test_list_for_user_context_filter_includes_matching_context_and_untargeted(preference_repository):
    preference_repository.add(
        _pref(
            "pref-item",
            type=PreferenceType.ITEM_DISLIKE,
            value="item-blazer-navy",
        )
    )
    preference_repository.add(
        _pref(
            "pref-context-dinner",
            type=PreferenceType.CONTEXT_DISLIKE,
            value="blazer",
            context="dinner",
        )
    )
    preference_repository.add(
        _pref(
            "pref-context-work",
            type=PreferenceType.CONTEXT_DISLIKE,
            value="blazer",
            context="work",
        )
    )

    results = preference_repository.list_for_user(USER_ID, context="client dinner")

    assert {p.id for p in results} == {"pref-item", "pref-context-dinner"}


def test_list_for_user_excludes_inactive_by_default(preference_repository):
    preference_repository.add(_pref("pref-1", active=False))

    assert preference_repository.list_for_user(USER_ID) == []
    assert len(preference_repository.list_for_user(USER_ID, active_only=False)) == 1
