from ornatus.tools.feedback_tools import make_feedback_tools

USER_ID = "user-1"


def test_record_feedback_tool_persists(feedback_service):
    (record_feedback,) = make_feedback_tools(feedback_service, USER_ID)

    result = record_feedback(
        feedback_text="I don't want to wear the blazer.",
        rejected_item_ids=["item-blazer"],
        preference_signal="mixed",
    )

    assert result["feedback_text"] == "I don't want to wear the blazer."
    assert result["rejected_item_ids"] == ["item-blazer"]
    assert result["preference_signal"] == "mixed"


def test_record_feedback_tool_persists_broader_preference_signals(feedback_service, preference_service):
    (record_feedback,) = make_feedback_tools(feedback_service, USER_ID)

    record_feedback(
        feedback_text="I don't like blazers for client dinners.",
        rejected_item_ids=["item-blazer"],
        preference_signals=[
            {"type": "context_dislike", "value": "blazer", "context": "client dinner"}
        ],
    )

    preferences = preference_service.get_preferences(USER_ID)
    values_by_type = {p.type.value: p.value for p in preferences}

    assert values_by_type["item_dislike"] == "item-blazer"
    assert values_by_type["context_dislike"] == "blazer"
