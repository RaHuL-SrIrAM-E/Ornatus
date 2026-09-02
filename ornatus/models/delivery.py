from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from ornatus.models._util import utc_now


class DeliveryStatus(StrEnum):
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class Delivery(BaseModel):
    id: str
    purchase_id: str
    carrier: str | None = None
    tracking_number: str | None = None
    status: DeliveryStatus = DeliveryStatus.IN_TRANSIT
    expected_date: date | None = None
    actual_date: date | None = None
    updated_at: datetime = Field(default_factory=utc_now)
