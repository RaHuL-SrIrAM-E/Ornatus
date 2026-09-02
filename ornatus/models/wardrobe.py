from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now
from ornatus.models.common import Formality, Season


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
    name: str
    category: ItemCategory
    subcategory: str | None = None
    colors: list[str] = Field(default_factory=list)
    pattern: str | None = None
    material: str | None = None
    brand: str | None = None
    size: str | None = None
    fit: str | None = None
    formality: Formality = Formality.CASUAL
    season: list[Season] = Field(default_factory=lambda: [Season.ALL_SEASON])
    suitable_occasions: list[str] = Field(default_factory=list)
    style_tags: list[str] = Field(default_factory=list)
    # image_urls stays a plain list of URLs today; this is deliberately the
    # only extension point future image-based ingestion needs — a pipeline
    # that populates an item from a photo just needs to fill in the fields
    # above plus one or more image_urls, nothing about the shape changes.
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
