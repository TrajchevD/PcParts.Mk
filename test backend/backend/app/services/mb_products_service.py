from app.db import fetchall

MB_CATEGORY_ID = 1

def list_motherboards(filters, sort, limit, offset):
    filters = filters or {}
    where = ["p.category_id = %s"]
    params = [MB_CATEGORY_ID]

    if filters.get("socket"):
        where.append("m.socket = %s")
        params.append(filters["socket"])

    if filters.get("memory_type"):
        where.append("m.memory_type = %s")
        params.append(filters["memory_type"])

    if filters.get("form_factor"):
        where.append("m.form_factor = %s")
        params.append(filters["form_factor"])

    if filters.get("min_price"):
        where.append("po.price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("po.price <= %s")
        params.append(filters["max_price"])

    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      m.product_id,
      m.model,
      m.socket,
      m.memory_type,
      m.form_factor,
      MIN(po.price) AS price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url) AS image_url
    FROM mb_specs_v2 m
    JOIN products p ON p.product_id = m.product_id
    JOIN product_offers po ON po.product_id = m.product_id
    WHERE {" AND ".join(where)}
      AND po.price IS NOT NULL
      AND po.currency = 'MKD'
    GROUP BY
      m.product_id,
      m.model,
      m.socket,
      m.memory_type,
      m.form_factor
    ORDER BY price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))




def get_mb_details(product_id: int):
    specs_sql = """
    SELECT *
    FROM mb_specs_v2
    WHERE product_id = %s
    """
    specs = fetchall(specs_sql, (product_id,))
    if not specs:
        return None

    offers_sql = """
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
    """
    offers = fetchall(offers_sql, (product_id,))

    return {
        "product_id": product_id,
        "specs": specs[0],
        "offers": offers,
    }
