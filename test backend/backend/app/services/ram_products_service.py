from app.db import fetchall

RAM_CATEGORY_ID = 3

def list_rams(filters, limit, offset):
    filters = filters or {}
    where = ["p.category_id = %s"]
    params = [RAM_CATEGORY_ID]

    if filters.get("memory_type"):
        where.append("r.memory_type = %s")
        params.append(filters["memory_type"])

    if filters.get("min_capacity"):
        where.append("r.total_capacity_gb >= %s")
        params.append(filters["min_capacity"])

    if filters.get("min_price"):
        where.append("po.price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("po.price <= %s")
        params.append(filters["max_price"])

    sql = f"""
    SELECT
      r.product_id,
      r.model,
      r.memory_type,
      r.speed_mhz,
      r.total_capacity_gb,
      r.kit_modules,
      po.price,
      po.image_url
    FROM ram_specs_v2 r
    JOIN products p ON p.product_id = r.product_id
    JOIN product_offers po ON po.product_id = r.product_id
    WHERE {" AND ".join(where)}
      AND po.price IS NOT NULL
      AND po.currency = 'MKD'
    ORDER BY po.price ASC
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))


def get_ram_details(product_id: int):
    specs = fetchall("""
        SELECT *
        FROM ram_specs_v2
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
