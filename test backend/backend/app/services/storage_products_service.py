from app.db import fetchall

STORAGE_CATEGORY_ID = 5


def list_storage(filters, sort, limit, offset):
    filters = filters or {}
    where = ["p.category_id = %s"]
    params = [STORAGE_CATEGORY_ID]

    if filters.get("storage_type"):
        where.append("s.storage_type = %s")
        params.append(filters["storage_type"])

    if filters.get("min_capacity"):
        where.append("s.capacity_gb >= %s")
        params.append(filters["min_capacity"])

    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      s.product_id,
      s.model,
      s.storage_type,
      s.capacity_gb,
      s.interface,
      s.form_factor,
      s.protocol,
      po.price,
      po.image_url
    FROM storage_specs_v2 s
    JOIN products p ON p.product_id = s.product_id
    JOIN product_offers po ON po.product_id = s.product_id
    WHERE {" AND ".join(where)}
      AND po.price IS NOT NULL
      AND po.currency = 'MKD'
    ORDER BY price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))


def get_storage_details(product_id: int):
    specs = fetchall("""
        SELECT *
        FROM storage_specs_v2
        WHERE product_id = %s
    """, (product_id,))

    if not specs:
        return None

    offers = fetchall("""
        SELECT
          po.offer_id,
          po.store_id,
          s.name AS store_name,
          po.price,
          po.currency,
          po.product_url,
          po.in_stock,
          po.image_url
        FROM product_offers po
        JOIN stores s ON s.store_id = po.store_id
        WHERE po.product_id = %s
          AND po.price IS NOT NULL
          AND po.currency = 'MKD'
        ORDER BY po.price ASC
    """, (product_id,))

    return {
        "product_id": product_id,
        "specs": specs[0],
        "offers": offers,
    }
