from ornatus.agent.orchestrator import build_orchestrator


def test_build_orchestrator_wires_wardrobe_tool(db):
    agent = build_orchestrator(db=db)

    assert "get_wardrobe_items" in agent.tool_names
