import pytest

from ornatus.persistence.database import Database
from ornatus.persistence.repositories.wardrobe_repository import WardrobeRepository
from ornatus.services.wardrobe_service import WardrobeService


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
