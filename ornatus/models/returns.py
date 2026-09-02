from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class ReturnStatus(StrEnum):
    INITIATED = "initiated"
    LABEL_CREATED = "label_created"
    SHIPPED = "shipped"
    REFUNDED = "refunded"


class ReturnRequest(BaseModel):
    id: str
    purchase_id: str
    item_id: str | None = None
    reason: str
    status: ReturnStatus = ReturnStatus.INITIATED
    refund_amount: float | None = None
    initiated_at: datetime = Field(default_factory=utc_now)
