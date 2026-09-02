"""CLI entrypoint for Ornatus.

    user request -> Ornatus agent -> tools (context/weather/wardrobe) ->
    reasoning -> outfit recommendation -> decision log -> response

Run with: poetry run ornatus "What should I wear to my client dinner Friday?"

Set ORNATUS_MODEL_PROVIDER=local to run this without AWS credentials, using
the deterministic local stand-in model (see ornatus/agent/local_model.py)
instead of real Bedrock/Nova.
"""

import logging
import sys

from ornatus.agent.orchestrator import build_runtime
from ornatus.api.demo_data import DEMO_USER_ID, seed_demo_wardrobe
from ornatus.config.logging import configure_logging
from ornatus.workflows.decision_logging import run_agent_and_log

DEFAULT_MESSAGE = "What should I wear to my client dinner Friday?"

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()

    runtime = build_runtime()
    seed_demo_wardrobe(runtime.wardrobe_service)

    message = " ".join(sys.argv[1:]) or DEFAULT_MESSAGE
    result = run_agent_and_log(runtime.agent, runtime.decision_service, DEMO_USER_ID, message)

    logger.info(
        "Decision logged: id=%s type=%s tools=%s outcome=%s",
        result.decision.id,
        result.decision.decision_type,
        result.decision.tools_used,
        result.decision.outcome,
    )


if __name__ == "__main__":
    main()
