"""
backfill_model_keys.py — fill model_key for existing products and merge duplicates.

Run once:  python backfill_model_keys.py
"""
import logging
from db import fetchall, execute, get_conn
from normalizer import extract_model_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("backfill")


def _merge(keep_id: int, drop_id: int) -> None:
    """Move all offers from drop_id to keep_id, then delete drop_id."""
    existing_stores = {
        r["store_id"]
        for r in fetchall("SELECT store_id FROM product_offers WHERE product_id = %s", (keep_id,))
    }

    drop_offers = fetchall(
        "SELECT offer_id, store_id FROM product_offers WHERE product_id = %s", (drop_id,)
    )

    for offer in drop_offers:
        if offer["store_id"] not in existing_stores:
            execute(
                "UPDATE product_offers SET product_id = %s WHERE offer_id = %s",
                (keep_id, offer["offer_id"]),
            )
        else:
            # Both products have an offer from the same store — drop the duplicate's offer
            execute("DELETE FROM offer_price_history WHERE offer_id = %s", (offer["offer_id"],))
            execute("DELETE FROM product_offers WHERE offer_id = %s", (offer["offer_id"],))

    # Drop spec row if present (keep_id's spec row takes priority)
    for tbl in ("cpu_specs", "gpu_specs", "mb_specs", "ram_specs", "storage_specs"):
        execute(f"DELETE FROM {tbl} WHERE product_id = %s", (drop_id,))

    execute("DELETE FROM products WHERE product_id = %s", (drop_id,))


def run():
    products = fetchall("""
        SELECT p.product_id, p.canonical_title, c.slug AS category
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE p.model_key IS NULL
    """)

    log.info(f"{len(products)} products with no model_key")
    updated = merged = skipped = 0

    for p in products:
        key = extract_model_key(p["canonical_title"], p["category"])
        if not key:
            skipped += 1
            continue

        # Try to set model_key directly
        try:
            execute(
                "UPDATE products SET model_key = %s WHERE product_id = %s AND model_key IS NULL",
                (key, p["product_id"]),
            )
            updated += 1
            continue
        except Exception:
            pass

        # Duplicate exists — find the keeper and merge
        rows = fetchall(
            "SELECT product_id FROM products WHERE model_key = %s AND category_id = ("
            "  SELECT category_id FROM categories WHERE slug = %s LIMIT 1"
            ") LIMIT 1",
            (key, p["category"]),
        )
        if not rows:
            skipped += 1
            continue

        keep_id = rows[0]["product_id"]
        try:
            _merge(keep_id, p["product_id"])
            merged += 1
            log.debug(f"  merged pid={p['product_id']} → pid={keep_id}  key={key}")
        except Exception as exc:
            log.warning(f"  merge failed pid={p['product_id']}: {exc}")
            skipped += 1

    log.info(f"Done — updated={updated}  merged={merged}  skipped={skipped}")


if __name__ == "__main__":
    run()
