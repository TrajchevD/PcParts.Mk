import json

from fastapi import APIRouter, Depends, HTTPException

from app.core.db import execute, fetchall
from app.core.deps import get_current_user
from app.schemas.alerts import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _parse_notifications(rows: list[dict]) -> list[dict]:
    for row in rows:
        raw = row.get("payload")
        if isinstance(raw, str):
            row["payload"] = json.loads(raw)
        elif raw is None:
            row["payload"] = []
        # MySQL JSON column already returns dict/list in newer drivers
        row["is_read"] = bool(row.get("is_read"))
    return rows


@router.get("", response_model=list[NotificationOut])
def list_notifications(user=Depends(get_current_user)):
    rows = fetchall(
        """
        SELECT *
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user["user_id"],),
    )
    return _parse_notifications(rows)


@router.post("/{notification_id}/read", status_code=200)
def mark_as_read(notification_id: int, user=Depends(get_current_user)):
    row = fetchall(
        "SELECT notification_id FROM notifications WHERE notification_id = %s AND user_id = %s",
        (notification_id, user["user_id"]),
    )
    if not row:
        raise HTTPException(404, "Notification not found")
    execute(
        "UPDATE notifications SET is_read = 1 WHERE notification_id = %s AND user_id = %s",
        (notification_id, user["user_id"]),
    )
    return {"ok": True}
