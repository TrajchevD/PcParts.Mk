from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class AlertCreateIn(BaseModel):
    alert_name: str
    category_slug: str
    title_query: str
    max_price: float
    store_name: Optional[str] = None

    @field_validator("max_price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("max_price must be positive")
        return v

    @field_validator("category_slug")
    @classmethod
    def valid_slug(cls, v: str) -> str:
        allowed = {"cpu", "gpu", "mb", "ram", "storage"}
        if v not in allowed:
            raise ValueError(f"category_slug must be one of {allowed}")
        return v


class AlertOut(BaseModel):
    alert_id: int
    alert_name: str
    category_slug: str
    title_query: str
    max_price: float
    store_name: Optional[str] = None
    status: str
    triggered_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    notification_id: int
    alert_id: Optional[int] = None
    title: str
    message: str
    payload: list[dict[str, Any]]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
