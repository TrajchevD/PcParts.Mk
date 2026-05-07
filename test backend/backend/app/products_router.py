from fastapi import APIRouter, Query
from typing import Optional, Literal
from app.db import get_conn

router = APIRouter(prefix="/api", tags=["products"])

SortType = Literal[
    "price_asc",
    "price_desc",
    "newest",
    "title_asc",
    "title_desc",
]


# =========================
# CATEGORIES
# =========================
@router.get("/categories")
def get_categories():
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
                c.slug AS category,
                COUNT(DISTINCT o.product_id) AS count
            FROM product_offers o
            JOIN products p ON p.product_id = o.product_id
            JOIN categories c ON c.category_id = p.category_id
            WHERE o.in_stock = 1
            GROUP BY c.slug
            ORDER BY c.slug ASC
        """)
        return cur.fetchall()
    finally:
        conn.close()


# =========================
# PRODUCTS
# =========================
@router.get("/products")
def get_products(
    category: str = Query(...),
    q: Optional[str] = Query(None),
    store: Optional[str] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    sort: SortType = Query("price_asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
):
    where = [
        "c.slug = %s",
        "o.in_stock = 1",
    ]
    params = [category]

    if q:
        where.append("o.title_raw LIKE %s")
        params.append(f"%{q}%")

    if store:
        where.append("s.name = %s")
        params.append(store)

    if price_min is not None:
        where.append("o.price >= %s")
        params.append(price_min)

    if price_max is not None:
        where.append("o.price <= %s")
        params.append(price_max)

    where_sql = " AND ".join(where)

    order_by = {
    "price_asc": "o.price ASC",
    "price_desc": "o.price DESC",
    "newest": "COALESCE(o.last_price_change_at, o.last_seen_at) DESC",
    "title_asc": "o.title_raw ASC",
    "title_desc": "o.title_raw DESC",
    }[sort]
    offset = (page - 1) * limit

    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        # ---------- COUNT ----------
        cur.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM product_offers o
            JOIN products p ON p.product_id = o.product_id
            JOIN stores s ON s.store_id = o.store_id
            JOIN categories c ON c.category_id = p.category_id
            WHERE {where_sql}
            """,
            params,
        )
        total = cur.fetchone()["total"]

        # ---------- DATA ----------
        data_params = params + [limit, offset]

        cur.execute(
            f"""
            SELECT
                o.offer_id            AS id,
                s.name                AS store,
                c.slug                AS category,
                o.title_raw           AS title,
                o.price               AS price,
                o.price_text_raw      AS price_text,
                o.product_url         AS link,
                o.image_url           AS image,
                o.in_stock            AS in_stock,
                o.created_at,
                o.last_seen_at,
                o.last_price_change_at
            FROM product_offers o
            JOIN products p ON p.product_id = o.product_id
            JOIN stores s ON s.store_id = o.store_id
            JOIN categories c ON c.category_id = p.category_id
            WHERE {where_sql}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
            """,
            data_params,
        )

        items = cur.fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
            "items": items,
        }

    finally:
        conn.close()
