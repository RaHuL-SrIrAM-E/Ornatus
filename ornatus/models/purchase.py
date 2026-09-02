from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class OrderStatus(StrEnum):
    NOT_ORDERED = "not_ordered"
    ORDERED = "ordered"
    CANCELLED = "cancelled"


class ProductCandidate(BaseModel):
    product_id: str
    title: str
    brand: str | None = None
    price: float
    currency: str = "USD"
    url: str | None = None
    image_url: str | None = None
    match_score: float | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class Purchase(BaseModel):
    id: str
    user_id: str
    trigger: str  # e.g. "manual_request" | "gap_fill" | "replacement"
    structured_requirement: dict[str, str] = Field(default_factory=dict)
    candidate_products: list[ProductCandidate] = Field(default_factory=list)
    selected_product: ProductCandidate | None = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_at: datetime | None = None
    order_status: OrderStatus = OrderStatus.NOT_ORDERED
    order_id: str | None = None
    cost: float | None = None
    created_at: datetime = Field(default_factory=utc_now)
