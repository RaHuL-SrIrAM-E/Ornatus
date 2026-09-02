"""Minimal CLI entrypoint for the Phase 1 milestone:

    user request -> Ornatus agent -> tool call -> structured data -> reasoning -> response

Run with: poetry run ornatus "what's in my wardrobe?"
"""

import sys

from ornatus.agent.orchestrator import build_orchestrator
from ornatus.api.demo_data import DEMO_USER_ID, seed_demo_wardrobe
from ornatus.config.logging import configure_logging
from ornatus.config.settings import get_settings
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.wardrobe_service import WardrobeService

DEFAULT_MESSAGE = f"What's currently in {DEMO_USER_ID}'s wardrobe?"


def main() -> None:
    configure_logging()

    db = Database(get_settings().db_path)
    db.initialize_schema()
    seed_demo_wardrobe(WardrobeService(WardrobeRepository(db)))

    message = " ".join(sys.argv[1:]) or DEFAULT_MESSAGE
    agent = build_orchestrator(db=db)
    agent(message)


if __name__ == "__main__":
    main()
