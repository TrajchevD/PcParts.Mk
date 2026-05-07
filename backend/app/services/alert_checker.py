"""
Alert checker service.

Checks active price alerts and creates in-app notifications when matching
in-stock offers are found under the user's max_price.

Optimisation: skips the full scan when offer_price_history hasn't changed
since the last run AND there are no reactivated alerts waiting for a first check.
"""

import json
import logging
from decimal import Decimal

from app.core.db import get_db

logger = logging.getLogger(__name__)


def _decimal_to_float(rows: list[dict]) -> list[dict]:
    return [
        {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}
        for row in rows
    ]


def _escape_like(value: str) -> str:
    """Escape MySQL LIKE special characters so user input is treated as literals."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _has_unchecked_active_alerts(cur) -> bool:
    """
    Returns True when any ACTIVE alert has no associated notification.
    This covers reactivated alerts (their notification was deleted on reactivation)
    as well as brand-new alerts that haven't been checked yet.
    """
    cur.execute(
        """
        SELECT 1
        FROM price_alerts pa
        LEFT JOIN notifications n ON n.alert_id = pa.alert_id
        WHERE pa.status = 'ACTIVE'
          AND n.notification_id IS NULL
        LIMIT 1
        """
    )
    return cur.fetchone() is not None


def run_alert_checks() -> dict:
    """
    Run the price-alert checker.

    Returns a summary dict:
        checked   – whether a full scan was performed
        changes   – whether price history had new entries (or unchecked alerts existed)
        triggered – number of alerts that matched and were marked TRIGGERED
    """
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        try:
            # 1. Get the last-run watermark
            cur.execute("SELECT last_checked_at FROM alert_state WHERE id = 1")
            state = cur.fetchone()
            last_checked = state["last_checked_at"] if state else None

            # 2. Skip the full scan only when BOTH conditions hold:
            #    (a) no new price history since last run
            #    (b) no active alerts are waiting for their first check
            if last_checked:
                cur.execute(
                    "SELECT 1 FROM offer_price_history WHERE changed_at > %s LIMIT 1",
                    (last_checked,),
                )
                price_history_changed = cur.fetchone() is not None
                unchecked_alerts_exist = _has_unchecked_active_alerts(cur)

                if not price_history_changed and not unchecked_alerts_exist:
                    logger.debug("Alert checker: no changes, skipping.")
                    return {"checked": True, "changes": False, "triggered": 0}

            # 3. Fetch all active alerts
            cur.execute(
                """
                SELECT alert_id, user_id, alert_name,
                       category_slug, title_query, store_name, max_price
                FROM price_alerts
                WHERE status = 'ACTIVE'
                """
            )
            alerts = cur.fetchall()

            triggered_count = 0

            for alert in alerts:
                # Escape LIKE wildcards so user-provided query is literal text
                safe_query = _escape_like(alert["title_query"])
                params: list = [
                    alert["category_slug"],
                    f"%{safe_query}%",
                    alert["max_price"],
                ]
                store_clause = ""
                if alert["store_name"]:
                    store_clause = "AND s.name = %s"
                    params.append(alert["store_name"])

                # 4. Find matching in-stock offers under max_price
                cur.execute(
                    f"""
                    SELECT
                      po.offer_id  AS id,
                      s.name       AS store,
                      c.slug       AS category,
                      po.title_raw AS title,
                      po.price,
                      po.price_text,
                      po.product_url AS link,
                      po.image_url   AS image
                    FROM product_offers po
                    JOIN products p   ON p.product_id  = po.product_id
                    JOIN stores s     ON s.store_id    = po.store_id
                    JOIN categories c ON c.category_id = p.category_id
                    WHERE c.slug = %s
                      AND po.in_stock = 1
                      AND po.title_raw LIKE %s ESCAPE '\\\\'
                      AND po.price <= %s
                      {store_clause}
                    ORDER BY po.price ASC
                    LIMIT %s
                    """,
                    tuple(params) + (8,),
                )
                matches = _decimal_to_float(cur.fetchall())

                if not matches:
                    continue

                # 5. Insert notification (INSERT IGNORE skips if already exists)
                cur.execute(
                    """
                    INSERT IGNORE INTO notifications
                      (user_id, alert_id, title, message, payload)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        alert["user_id"],
                        alert["alert_id"],
                        f"Price alert: {alert['alert_name']}",
                        f"Found {len(matches)} matching product(s) under your price.",
                        json.dumps(matches),
                    ),
                )

                # 6. Mark alert as triggered
                cur.execute(
                    """
                    UPDATE price_alerts
                    SET status = 'TRIGGERED', triggered_at = NOW()
                    WHERE alert_id = %s
                    """,
                    (alert["alert_id"],),
                )
                triggered_count += 1
                logger.info(
                    "Alert %d triggered for user %d — %d matches found.",
                    alert["alert_id"],
                    alert["user_id"],
                    len(matches),
                )

            # 7. Advance the watermark
            cur.execute(
                "UPDATE alert_state SET last_checked_at = NOW() WHERE id = 1"
            )

            return {"checked": True, "changes": True, "triggered": triggered_count}

        except Exception as exc:
            logger.exception("Alert checker failed: %s", exc)
            raise
        finally:
            cur.close()
