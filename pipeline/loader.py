import logging
import re
from decimal import Decimal, InvalidOperation
from db import get_conn
from normalizer import extract_model_key

log = logging.getLogger("pipeline.loader")

_PRICE_RE      = re.compile(r"[\d.,]+")
_EUROPEAN_FMT  = re.compile(r'^\d{1,3}(\.\d{3})+(,\d+)?$')
_SPACE_THOUSANDS = re.compile(r'\d{1,3}(?:\s\d{3})+(?:[.,]\d+)?')


def _parse_price(price_text: str, store: str) -> Decimal | None:
    if not price_text:
        return None
    text = price_text.replace("\xa0", " ")
    m = re.search(r'\d{1,3}(?:\.\d{3})+(?:,\d+)?', text)
    if m:
        raw = m.group(0).replace(".", "").replace(",", ".")
        try:
            return Decimal(raw)
        except InvalidOperation:
            pass
    m = _SPACE_THOUSANDS.search(text)
    if m:
        raw = re.sub(r'\s', '', m.group(0)).replace(",", ".")
        try:
            return Decimal(raw)
        except InvalidOperation:
            pass
    m = _PRICE_RE.search(text)
    if not m:
        return None
    raw = m.group(0).replace(",", "")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def mark_all_out_of_stock(store_name: str) -> None:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE product_offers po
            JOIN stores s ON s.store_id = po.store_id
            SET po.in_stock = 0
            WHERE s.name = %s
            """,
            (store_name,),
        )
        cur.close()
    finally:
        conn.close()


def upsert_offer(item: dict) -> None:
    price_val  = _parse_price(item.get("price", ""), item.get("store", ""))
    price_text = (item.get("price") or "").strip()
    category   = (item.get("category") or "").lower()
    model_key  = extract_model_key(item.get("title", ""), category)
    title      = item["title"]
    store_name = item["store"]

    conn = get_conn()
    try:
        conn.autocommit = False
        cur = conn.cursor(dictionary=True)

        # 1. Resolve or create store
        cur.execute("INSERT IGNORE INTO stores (name) VALUES (%s)", (store_name,))
        cur.execute("SELECT store_id FROM stores WHERE name = %s LIMIT 1", (store_name,))
        store_id = cur.fetchone()["store_id"]

        # 2. Resolve or create category
        cur.execute(
            "INSERT IGNORE INTO categories (slug, name) VALUES (%s, %s)",
            (category, category),
        )
        cur.execute(
            "SELECT category_id FROM categories WHERE slug = %s LIMIT 1",
            (category,),
        )
        category_id = cur.fetchone()["category_id"]

        # 3. Resolve or create product (match by model_key first, then title)
        product_id = None
        if model_key:
            cur.execute(
                "SELECT product_id FROM products WHERE model_key = %s AND category_id = %s LIMIT 1",
                (model_key, category_id),
            )
            row = cur.fetchone()
            if row:
                product_id = row["product_id"]

        if product_id is None:
            cur.execute(
                "SELECT product_id FROM products WHERE canonical_title = %s AND category_id = %s LIMIT 1",
                (title, category_id),
            )
            row = cur.fetchone()
            if row:
                product_id = row["product_id"]

        if product_id is None:
            cur.execute(
                "INSERT INTO products (category_id, canonical_title, model_key, spec_status) "
                "VALUES (%s, %s, %s, 'pending')",
                (category_id, title, model_key),
            )
            product_id = cur.lastrowid

        # 4. Capture existing offer for price-history comparison
        cur.execute(
            "SELECT offer_id, price FROM product_offers "
            "WHERE product_id = %s AND store_id = %s LIMIT 1",
            (product_id, store_id),
        )
        existing   = cur.fetchone()
        old_offer_id = existing["offer_id"] if existing else None
        old_price    = existing["price"]    if existing else None

        # 5. Upsert offer row
        cur.execute(
            """
            INSERT INTO product_offers
                (product_id, store_id, title_raw, price, price_text,
                 product_url, image_url, in_stock, last_seen_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1, NOW())
            ON DUPLICATE KEY UPDATE
                title_raw    = VALUES(title_raw),
                price        = VALUES(price),
                price_text   = VALUES(price_text),
                product_url  = VALUES(product_url),
                image_url    = VALUES(image_url),
                in_stock     = 1,
                last_seen_at = NOW(),
                updated_at   = NOW()
            """,
            (product_id, store_id, title, price_val, price_text,
             item.get("link"), item.get("image")),
        )

        # 6. Record price change in history
        if (old_offer_id and old_price is not None
                and price_val is not None and old_price != price_val):
            cur.execute(
                "INSERT INTO offer_price_history (offer_id, price) VALUES (%s, %s)",
                (old_offer_id, price_val),
            )

        conn.commit()
        cur.close()
    except Exception as exc:
        conn.rollback()
        log.warning(f"upsert failed for «{item.get('title')}»: {exc}")
        raise
    finally:
        conn.autocommit = True
        conn.close()
