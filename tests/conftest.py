import pytest

from ornatus.persistence.database import Database
from ornatus.persistence.repositories.agent_decision_repository import AgentDecisionRepository
from ornatus.persistence.repositories.feedback_repository import FeedbackRepository
from ornatus.persistence.repositories.outfit_recommendation_repository import (
    OutfitRecommendationRepository,
)
from ornatus.persistence.repositories.preference_repository import PreferenceRepository
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.decision_service import DecisionService
from ornatus.services.feedback_service import FeedbackService
from ornatus.services.outfit_service import OutfitService
from ornatus.services.preference_service import PreferenceService
from ornatus.services.wardrobe_service import WardrobeService

TEST_USER_ID = "user-1"


@pytest.fixture
def db():
    database = Database(":memory:")
    database.initialize_schema()
    yield database
    database.close()


@pytest.fixture
def wardrobe_repository(db):
    return WardrobeRepository(db)


@pytest.fixture
def wardrobe_service(wardrobe_repository):
    return WardrobeService(wardrobe_repository)


@pytest.fixture
def outfit_recommendation_repository(db):
    return OutfitRecommendationRepository(db)


@pytest.fixture
def outfit_service(outfit_recommendation_repository, wardrobe_repository):
    return OutfitService(outfit_recommendation_repository, wardrobe_repository)


@pytest.fixture
def preference_repository(db):
    return PreferenceRepository(db)


@pytest.fixture
def preference_service(preference_repository):
    return PreferenceService(preference_repository)


@pytest.fixture
def feedback_repository(db):
    return FeedbackRepository(db)


@pytest.fixture
def feedback_service(feedback_repository, outfit_service, preference_service):
    return FeedbackService(feedback_repository, outfit_service, preference_service)


@pytest.fixture
def agent_decision_repository(db):
    return AgentDecisionRepository(db)


@pytest.fixture
def decision_service(agent_decision_repository):
    return DecisionService(agent_decision_repository)
