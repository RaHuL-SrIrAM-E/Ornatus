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
