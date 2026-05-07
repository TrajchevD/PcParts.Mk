from fastapi import APIRouter, Depends
from app.db import get_conn
from app.auth.dependencies import get_current_user
from app.models.notification_models import NotificationOut
import json
from datetime import datetime 
router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(user=Depends(get_current_user)):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT *
            FROM notifications
            WHERE user_id=%s
            ORDER BY created_at DESC
            """,
            (user["user_id"],),
        )

        rows = cur.fetchall()

        for r in rows:
            for k, v in r.items():
                # convert datetime → string
                if isinstance(v, datetime):
                    r[k] = v.isoformat()

            # ✅ convert payload JSON string → list
            if isinstance(r.get("payload"), str):
                r["payload"] = json.loads(r["payload"])

        return rows

    finally:
        conn.close()


@router.post("/{notification_id}/read")
def mark_as_read(notification_id: int, user=Depends(get_current_user)):
    conn = get_conn()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE notifications
            SET is_read=1
            WHERE notification_id=%s AND user_id=%s
            """,
            (notification_id, user["user_id"]),
        )

        return {"ok": True}

    finally:
        conn.close()
