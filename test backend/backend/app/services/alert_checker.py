import json
from app.db import get_conn
from decimal import Decimal

def normalize_for_json(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        clean = {}
        for k, v in r.items():
            if isinstance(v, Decimal):
                clean[k] = float(v)   # or str(v)
            else:
                clean[k] = v
        out.append(clean)
    return out

def _get_last_checked_at(cur):
    cur.execute("SELECT last_checked_at FROM alert_state WHERE id=1")
    row = cur.fetchone()
    return row["last_checked_at"] if row else None


def _set_last_checked_at(cur):
    cur.execute("UPDATE alert_state SET last_checked_at = NOW() WHERE id=1")


def run_alert_checks() -> dict:
    """
    Checks alerts ONLY if the DB changed since last run.
    Uses offer_price_history.changed_at as change signal.
    Creates in-app notifications.
    Alerts trigger ONCE.
    """
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        last_checked = _get_last_checked_at(cur)

        # ---- CHECK IF DB CHANGED ----
        if last_checked:
            cur.execute(
                """
                SELECT 1
                FROM offer_price_history
                WHERE changed_at > %s
                LIMIT 1
                """,
                (last_checked,),
            )
            has_changes = cur.fetchone() is not None
        else:
            has_changes = True  # first run

        if not has_changes:
            return {"checked": True, "changes": False, "triggered": 0}

        # ---- FETCH ACTIVE ALERTS ----
        cur.execute(
            """
            SELECT
                alert_id,
                user_id,
                alert_name,
                category_slug,
                title_query,
                store_name,
                max_price
            FROM price_alerts
            WHERE status='ACTIVE'
            """
        )
        alerts = cur.fetchall()

        triggered_count = 0

        for a in alerts:
            params = [
                a["category_slug"],
                f"%{a['title_query']}%",
                a["max_price"],
            ]

            store_clause = ""
            if a["store_name"]:
                store_clause = "AND s.name = %s"
                params.append(a["store_name"])

            # ---- FIND MATCHING OFFERS ----
            cur.execute(
                f"""
                SELECT
                    o.offer_id AS id,
                    s.name AS store,
                    c.slug AS category,
                    o.title_raw AS title,
                    o.price AS price,
                    o.price_text_raw AS price_text,
                    o.product_url AS link,
                    o.image_url AS image
                FROM product_offers o
                JOIN products p ON p.product_id = o.product_id
                JOIN stores s ON s.store_id = o.store_id
                JOIN categories c ON c.category_id = p.category_id
                WHERE c.slug = %s
                  AND o.in_stock = 1
                  AND o.title_raw LIKE %s
                  AND o.price <= %s
                  {store_clause}
                ORDER BY o.price ASC
                LIMIT 8
                """,
                tuple(params),
            )

            matches = normalize_for_json(cur.fetchall())

            if not matches:
                continue

            # ---- CREATE IN-APP NOTIFICATION ----
            cur.execute(
                """
                INSERT IGNORE INTO notifications
                (user_id, alert_id, title, message, payload)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    a["user_id"],
                    a["alert_id"],
                    f"Price alert triggered: {a['alert_name']}",
                    f"We found {len(matches)} matching product(s).",
                    json.dumps(matches),
                ),
            )

            # ---- MARK ALERT AS TRIGGERED ----
            cur.execute(
                """
                UPDATE price_alerts
                SET status='TRIGGERED', triggered_at=NOW()
                WHERE alert_id=%s
                """,
                (a["alert_id"],),
            )

            triggered_count += 1

        # ---- UPDATE STATE ----
        _set_last_checked_at(cur)

        return {"checked": True, "changes": True, "triggered": triggered_count}

    finally:
        conn.close()
