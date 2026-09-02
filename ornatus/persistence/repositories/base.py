"""Repository abstraction.

Every domain repository (wardrobe, purchases, deliveries, ...) implements
this against ``Database``. Only ``WardrobeRepository`` exists concretely in
Phase 1; the abstraction is what lets the others be added later without
reshaping the persistence layer.
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
