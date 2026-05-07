from app.db import fetchall

CPU_MODEL_REGEX = (
    "(AMD Ryzen [3579] [0-9]{4}(X3D|X|G|F|AF)?|"
    "Intel Core i[3579]-[0-9]{5}(KF|K|F)?|"
    "Intel Core Ultra [57] [0-9]{3}(KF|K|F)?)"
)


CPU_CATEGORY_ID = 4  # use your real category id

def list_grouped_cpus(search, filters, sort, limit, offset):
    filters = filters or {}
    params = []
    where = ["1=1"]

    if search:
        where.append("x.model_key LIKE %s")
        params.append(f"%{search}%")

    if filters.get("brand"):
        where.append("cs.brand = %s")
        params.append(filters["brand"])

    if filters.get("socket"):
        where.append("cs.socket = %s")
        params.append(filters["socket"])

    if filters.get("min_cores"):
        where.append("cs.cores >= %s")
        params.append(filters["min_cores"])
      
    if filters.get("min_price"):
        where.append("x.price >= %s")
        params.append(filters["min_price"])
    
    if filters.get("max_price"):
        where.append("x.price <= %s")
        params.append(filters["max_price"])



    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      x.model_key AS cpu_model,
      cs.brand,
      cs.socket,
      cs.cores,
      MIN(x.price) AS min_price,
      COUNT(DISTINCT x.store_id) AS offer_count,
      MAX(x.image_url) AS image_url
    FROM (
      SELECT
        b.model_key,
        b.price,
        b.image_url,
        b.store_id
      FROM (
        -- base offers
        SELECT
          REGEXP_SUBSTR(po.title_raw, '{CPU_MODEL_REGEX}') AS model_key,
          po.price,
          po.image_url,
          po.store_id
        FROM product_offers po
        WHERE po.title_raw IS NOT NULL
          AND po.price IS NOT NULL
          AND po.currency = 'MKD'
      ) b
      JOIN (
        -- average price per CPU model
        SELECT
          REGEXP_SUBSTR(po.title_raw, '{CPU_MODEL_REGEX}') AS model_key,
          AVG(po.price) AS avg_price
        FROM product_offers po
        WHERE po.title_raw IS NOT NULL
          AND po.price IS NOT NULL
          AND po.currency = 'MKD'
        GROUP BY model_key
      ) a
        ON a.model_key = b.model_key
       AND b.price >= a.avg_price * 0.7
    ) x
    JOIN cpu_specs cs
      ON UPPER(cs.cpu_model) = UPPER(x.model_key)
    WHERE {" AND ".join(where)}
    GROUP BY
      x.model_key,
      cs.brand,
      cs.socket,
      cs.cores
    ORDER BY min_price {order}
    LIMIT %s OFFSET %s
    """




    params += [limit, offset]
    return fetchall(sql, tuple(params))

def get_cpu_details(cpu_model: str):
    # specs
    specs_sql = """
    SELECT
      cpu_model,
      brand,
      socket,
      cores,
      threads,
      base_clock_ghz,
      boost_clock_ghz,
      tdp_w,
      memory_type
    FROM cpu_specs
    WHERE UPPER(cpu_model) = UPPER(%s)
    """
    specs = fetchall(specs_sql, (cpu_model,))
    if not specs:
        return None

    # offers
    offers_sql = f"""
SELECT
  b.offer_id,
  b.store_id,
  s.name AS store_name,
  b.price,
  b.currency,
  b.product_url,
  b.in_stock,
  b.image_url,
  b.last_seen_at
FROM (
  SELECT
    po.offer_id,
    po.store_id,
    po.price,
    po.currency,
    po.product_url,
    po.in_stock,
    po.image_url,
    po.last_seen_at,
    REGEXP_SUBSTR(po.title_raw, '{CPU_MODEL_REGEX}') AS model_key
  FROM product_offers po
  WHERE po.price IS NOT NULL
    AND po.currency = 'MKD'
) b
JOIN (
  SELECT
    REGEXP_SUBSTR(po.title_raw, '{CPU_MODEL_REGEX}') AS model_key,
    AVG(po.price) AS avg_price
  FROM product_offers po
  WHERE po.price IS NOT NULL
    AND po.currency = 'MKD'
  GROUP BY model_key
) a
  ON a.model_key = b.model_key
 AND b.price >= a.avg_price * 0.7
JOIN stores s
  ON s.store_id = b.store_id
WHERE b.model_key = %s
ORDER BY b.price ASC

"""
    offers = fetchall(offers_sql, (cpu_model,))

    return {
        "cpu_model": cpu_model,
        "specs": specs[0],
        "offers": offers,
    }
