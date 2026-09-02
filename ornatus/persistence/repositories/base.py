"""Repository abstraction.

Every domain repository (wardrobe, outfit recommendations, decisions,
feedback, ...) implements this against ``Database``. Domain-specific query
methods (filters, "mark worn", "latest for user", ...) live on the concrete
repository, not here — this abstraction only holds what every repository
needs.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class Repository(ABC, Generic[ModelT]):
    @abstractmethod
    def add(self, item: ModelT) -> ModelT: ...

    @abstractmethod
    def get(self, item_id: str) -> ModelT | None: ...

    @abstractmethod
    def list_for_user(self, user_id: str) -> list[ModelT]: ...
