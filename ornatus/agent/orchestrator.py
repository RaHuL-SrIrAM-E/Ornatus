"""The single Ornatus orchestrating agent.

Phase 1 has exactly one Strands Agent. It is wired here with whatever tools
exist so far; new domains add to ``_default_tools`` (or are passed in
explicitly for tests) rather than becoming new agents. Nothing below assumes
there will only ever be one agent — ``build_orchestrator`` just doesn't need
more than one yet.
"""

from dataclasses import dataclass

from strands import Agent

from ornatus.agent.model_provider import get_model
from ornatus.agent.system_prompt import SYSTEM_PROMPT
from ornatus.config.settings import get_settings
from ornatus.persistence.database import Database
from ornatus.persistence.repositories.agent_decision_repository import AgentDecisionRepository
from ornatus.persistence.repositories.feedback_repository import FeedbackRepository
from ornatus.persistence.repositories.outfit_recommendation_repository import (
    OutfitRecommendationRepository,
)
from ornatus.persistence.repositories.preference_repository import PreferenceRepository
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.calendar_service import CalendarService
from ornatus.services.decision_service import DecisionService
from ornatus.services.feedback_service import FeedbackService
from ornatus.services.outfit_service import OutfitService
from ornatus.services.preference_service import PreferenceService
from ornatus.services.wardrobe_service import WardrobeService
from ornatus.services.weather_service import WeatherService
from ornatus.tools.context_tools import make_context_tools
from ornatus.tools.feedback_tools import make_feedback_tools
from ornatus.tools.outfit_tools import make_outfit_tools
from ornatus.tools.preference_tools import make_preference_tools
from ornatus.tools.wardrobe_tools import make_wardrobe_tools


@dataclass
class OrnatusRuntime:
    """Everything a caller (the CLI, a trigger, a test) needs to run the
    agent and log the outcome — the agent plus the services that sit
    outside the tool-calling loop.
    """

    agent: Agent
    user_id: str
    wardrobe_service: WardrobeService
    outfit_service: OutfitService
    feedback_service: FeedbackService
    preference_service: PreferenceService
    decision_service: DecisionService


def _default_tools(
    db: Database, user_id: str
) -> tuple[list, WardrobeService, OutfitService, FeedbackService, PreferenceService]:
    wardrobe_service = WardrobeService(WardrobeRepository(db))
    outfit_service = OutfitService(OutfitRecommendationRepository(db), WardrobeRepository(db))
    preference_service = PreferenceService(PreferenceRepository(db))
    feedback_service = FeedbackService(FeedbackRepository(db), outfit_service, preference_service)
    calendar_service = CalendarService()
    weather_service = WeatherService()

    tools = [
        *make_wardrobe_tools(wardrobe_service, user_id),
        *make_context_tools(calendar_service, weather_service),
        *make_preference_tools(preference_service, user_id),
        *make_outfit_tools(outfit_service, user_id),
        *make_feedback_tools(feedback_service, user_id),
    ]
    return tools, wardrobe_service, outfit_service, feedback_service, preference_service


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
        tools, *_ = _default_tools(db, get_settings().current_user_id)

    return Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        name="ornatus",
        description="Autonomous personal wardrobe agent.",
    )


def build_runtime(db: Database | None = None) -> OrnatusRuntime:
    """Construct the orchestrator plus the services needed to log decisions.

    This is what the CLI (and anything else driving real conversations)
    should use; ``build_orchestrator`` alone is for tests that only care
    about the agent/tool wiring.
    """
    settings = get_settings()
    db = db or Database(settings.db_path)
    db.initialize_schema()
    user_id = settings.current_user_id

    tools, wardrobe_service, outfit_service, feedback_service, preference_service = _default_tools(
        db, user_id
    )
    decision_service = DecisionService(AgentDecisionRepository(db))
    agent = build_orchestrator(db=db, tools=tools)

    return OrnatusRuntime(
        agent=agent,
        user_id=user_id,
        wardrobe_service=wardrobe_service,
        outfit_service=outfit_service,
        feedback_service=feedback_service,
        preference_service=preference_service,
        decision_service=decision_service,
    )
