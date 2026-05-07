from fastapi import APIRouter, Depends, HTTPException

from app.core.db import execute, fetchall, fetchone
from app.core.deps import get_current_user, require_admin_key
from app.schemas.alerts import AlertCreateIn, AlertOut
from app.services.alert_checker import run_alert_checks

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut, status_code=201)
def create_alert(body: AlertCreateIn, user=Depends(get_current_user)):
    alert_id = execute(
        """
        INSERT INTO price_alerts
          (user_id, alert_name, category_slug, title_query, store_name, max_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
        """,
        (
            user["user_id"],
            body.alert_name,
            body.category_slug,
            body.title_query,
            body.store_name,
            body.max_price,
        ),
    )
    row = fetchone(
        "SELECT * FROM price_alerts WHERE alert_id = %s",
        (alert_id,),
    )
    return row


@router.get("", response_model=list[AlertOut])
def list_alerts(user=Depends(get_current_user)):
    return fetchall(
        """
        SELECT * FROM price_alerts
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user["user_id"],),
    )


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, user=Depends(get_current_user)):
    row = fetchone(
        "SELECT * FROM price_alerts WHERE alert_id = %s AND user_id = %s",
        (alert_id, user["user_id"]),
    )
    if not row:
        raise HTTPException(404, "Alert not found")
    return row


@router.post("/{alert_id}/reactivate", response_model=AlertOut)
def reactivate_alert(alert_id: int, user=Depends(get_current_user)):
    """
    Reset a TRIGGERED alert back to ACTIVE so it can fire again.

    Also deletes the existing notification for this alert (so the INSERT IGNORE
    in alert_checker can create a fresh one) and resets the global alert_state
    watermark so the checker will rescan current prices immediately.
    """
    row = fetchone(
        "SELECT * FROM price_alerts WHERE alert_id = %s AND user_id = %s",
        (alert_id, user["user_id"]),
    )
    if not row:
        raise HTTPException(404, "Alert not found")

    # Clear the old notification so the checker can create a new one
    execute(
        "DELETE FROM notifications WHERE alert_id = %s AND user_id = %s",
        (alert_id, user["user_id"]),
    )

    # Reset the alert to ACTIVE and clear its trigger timestamp
    execute(
        """
        UPDATE price_alerts
        SET status = 'ACTIVE', triggered_at = NULL
        WHERE alert_id = %s
        """,
        (alert_id,),
    )

    # Reset the global watermark so the next checker run rescans all current prices.
    # This ensures the reactivated alert sees current offers even if no new price
    # history entries exist since the last run.
    execute("UPDATE alert_state SET last_checked_at = NULL WHERE id = 1")

    return fetchone(
        "SELECT * FROM price_alerts WHERE alert_id = %s",
        (alert_id,),
    )


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: int, user=Depends(get_current_user)):
    row = fetchone(
        "SELECT alert_id FROM price_alerts WHERE alert_id = %s AND user_id = %s",
        (alert_id, user["user_id"]),
    )
    if not row:
        raise HTTPException(404, "Alert not found")
    execute(
        "DELETE FROM price_alerts WHERE alert_id = %s",
        (alert_id,),
    )


@router.post(
    "/check",
    tags=["admin"],
    dependencies=[Depends(require_admin_key)],
    summary="Trigger the price-alert checker (admin only)",
)
def trigger_alert_check():
    """
    Manually runs the price-alert checker.

    Requires the X-API-Key header to equal the server's ADMIN_API_KEY.
    In production this endpoint should be called by an external cron job or
    the background scheduler instead of being exposed publicly.
    """
    return run_alert_checks()
