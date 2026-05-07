from fastapi import APIRouter, Depends, HTTPException
from app.db import get_conn
from app.auth.dependencies import get_current_user
from app.models.alert_models import AlertCreateIn, AlertOut
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut)
def create_alert(data: AlertCreateIn, user=Depends(get_current_user)):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            INSERT INTO price_alerts
            (user_id, alert_name, category_slug, title_query, store_name, max_price, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
            """,
            (
                user["user_id"],
                data.alert_name,
                data.category_slug,
                data.title_query,
                data.store_name,
                data.max_price,
            ),
        )

        alert_id = cur.lastrowid

        cur.execute(
            "SELECT * FROM price_alerts WHERE alert_id=%s",
            (alert_id,),
        )

        return cur.fetchone()

    finally:
        conn.close()


@router.get("")
def list_alerts(user=Depends(get_current_user)):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT
                alert_id,
                alert_name,
                category_slug,
                title_query,
                max_price,
                store_name,
                status,
                triggered_at
            FROM price_alerts
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user["user_id"],),
        )

        rows = cur.fetchall()

        # ✅ FIX: serialize datetime
        for r in rows:
            for k, v in r.items():
                if isinstance(v, datetime):
                    r[k] = v.isoformat()
        

        return rows

    finally:
        conn.close()
