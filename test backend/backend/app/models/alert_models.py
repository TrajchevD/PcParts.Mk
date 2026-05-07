from pydantic import BaseModel
from typing import Optional


class AlertCreateIn(BaseModel):
    alert_name: str
    category_slug: str
    title_query: str
    max_price: float
    store_name: Optional[str] = None


class AlertOut(BaseModel):
    alert_id: int
    alert_name: str
    category_slug: str
    title_query: str
    max_price: float
    store_name: Optional[str]
    status: str
    triggered_at: Optional[str]
