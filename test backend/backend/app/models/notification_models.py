from pydantic import BaseModel
from typing import Any, List, Dict


class NotificationOut(BaseModel):
    notification_id: int
    alert_id: int
    title: str
    message: str
    payload: List[Dict[str, Any]]
    is_read: int
    created_at: str
