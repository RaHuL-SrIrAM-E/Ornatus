"""The single Ornatus orchestrating agent.

Phase 1 has exactly one Strands Agent. It is wired here with whatever tools
exist so far; new domains add to ``_default_tools`` (or are passed in
explicitly for tests) rather than becoming new agents. Nothing below assumes
there will only ever be one agent — ``build_orchestrator`` just doesn't need
more than one yet.
"""

from strands import Agent

from ornatus.agent.model_provider import get_model
from ornatus.agent.system_prompt import SYSTEM_PROMPT
from ornatus.config.settings import get_settings
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.wardrobe_service import WardrobeService
from ornatus.tools.wardrobe_tools import make_wardrobe_tools


def _default_tools(db: Database) -> list:
    wardrobe_service = WardrobeService(WardrobeRepository(db))
    return [*make_wardrobe_tools(wardrobe_service)]


def build_orchestrator(db: Database | None = None, tools: list | None = None) -> Agent:
    """Construct the Ornatus orchestrator.

    Args:
        db: Database to wire default tools against. Defaults to the
            configured SQLite path. Ignored if ``tools`` is given.
        tools: Explicit tool list, for tests or alternate wiring. When
            omitted, the default tool set is built from ``db``.
    """
    if tools is None:
        db = db or Database(get_settings().db_path)
        db.initialize_schema()
        tools = _default_tools(db)

    return Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        name="ornatus",
        description="Autonomous personal wardrobe agent.",
    )
