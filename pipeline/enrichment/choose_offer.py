from db import fetchall


def pick_best_offer(product_id: int) -> dict | None:
    """
    Return the best offer URL to fetch specs from.
    Prefers: in-stock > Anhoch (richest spec descriptions) > lowest price.
    """
    rows = fetchall(
        """
        SELECT po.offer_id, po.product_id, po.product_url, po.title_raw,
               po.in_stock, po.price, s.name AS store_name
        FROM product_offers po
        JOIN stores s ON s.store_id = po.store_id
        WHERE po.product_id = %s
          AND po.product_url IS NOT NULL
          AND po.product_url <> ''
        ORDER BY
            po.in_stock DESC,
            (s.name = 'Anhoch') DESC,
            po.price ASC
        LIMIT 1
        """,
        (product_id,),
    )
    return rows[0] if rows else None
