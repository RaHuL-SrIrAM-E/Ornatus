from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class ItemCategory(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    OUTERWEAR = "outerwear"
    DRESS = "dress"
    SHOES = "shoes"
    ACCESSORY = "accessory"


class ItemStatus(StrEnum):
    ACTIVE = "active"
    LAUNDRY = "laundry"
    REPAIR = "repair"
    DONATED = "donated"
    RETIRED = "retired"


class WardrobeItem(BaseModel):
    id: str
    user_id: str
    category: ItemCategory
    subcategory: str | None = None
    colors: list[str] = Field(default_factory=list)
    pattern: str | None = None
    fabric: str | None = None
    brand: str | None = None
    size: str | None = None
    fit: str | None = None
    tags: list[str] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    purchase_date: date | None = None
    purchase_price: float | None = None
    source: str = "manual"  # "manual" | "purchased_via_ornatus"
    status: ItemStatus = ItemStatus.ACTIVE
    wear_count: int = 0
    last_worn_date: date | None = None
    condition: str | None = None
    care_instructions: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class WardrobeSnapshot(BaseModel):
    """A derived, point-in-time view over a user's wardrobe.

    Not persisted directly — computed on demand from WardrobeItem rows.
    """

    user_id: str
    total_items: int
    items_in_laundry: int
    items_needing_repair: int
    category_counts: dict[str, int] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=utc_now)
