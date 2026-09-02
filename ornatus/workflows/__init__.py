"""Orchestration that spans a whole agent turn (or, later, longer-lived
processes like purchase approval -> order -> delivery -> wardrobe add).

``decision_logging.run_agent_and_log`` is the first thing here: it invokes
the orchestrator and turns the resulting conversation into a persisted
``AgentDecision`` for observability. Multi-step processes that outlive a
single turn (returns, purchase approval) are still reserved for later.
"""
