from ornatus.models.decision import DecisionOutcome, DecisionType

USER_ID = "user-1"


def test_record_persists_decision(decision_service):
    decision = decision_service.record(
        user_id=USER_ID,
        user_request="What should I wear to my client dinner Friday?",
        decision_type=DecisionType.OUTFIT_RECOMMENDATION,
        tools_used=["get_event_context", "get_weather", "get_wardrobe_items", "record_outfit_recommendation"],
        reasoning_summary="Picked a business-casual outfit for a cool Friday evening.",
        selected_item_ids=["item-1", "item-2"],
    )

    assert decision.id
    assert decision.outcome == DecisionOutcome.COMPLETED
    assert decision.selected_item_ids == ["item-1", "item-2"]


def test_list_for_user_returns_recorded_decisions(decision_service):
    decision_service.record(
        user_id=USER_ID,
        user_request="req 1",
        decision_type=DecisionType.OTHER,
        tools_used=[],
        reasoning_summary="n/a",
    )
    decision_service.record(
        user_id=USER_ID,
        user_request="req 2",
        decision_type=DecisionType.FEEDBACK,
        tools_used=["record_feedback"],
        reasoning_summary="n/a",
    )

    decisions = decision_service.list_for_user(USER_ID)

    assert len(decisions) == 2
    assert {d.user_request for d in decisions} == {"req 1", "req 2"}
