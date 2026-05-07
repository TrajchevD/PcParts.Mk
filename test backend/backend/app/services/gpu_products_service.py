from app.db import fetchall

GPU_MODEL_REGEX = (
    "(RTX\\s?(?:20|30|40|50)[0-9]{2,3}\\s?(?:Ti|SUPER)?|"
    "RX\\s?[5679][0-9]{3,4}\\s?(?:XT|XTX)?)"
)

from app.db import fetchall

def list_grouped_gpus(search, filters, sort, limit, offset):
    filters = filters or {}
    params = []
    where = ["x.model_key IS NOT NULL"]

    # 🔎 Search
    if search:
        where.append("x.model_key LIKE %s")
        params.append(f"%{search}%")

    # 🏷️ Brand filter (FIXED)
    if filters.get("brand") == "NVIDIA":
        where.append("x.model_key LIKE 'RTX%'")

    if filters.get("brand") == "AMD":
        where.append("x.model_key LIKE 'Radeon RX %'")

    # 💾 VRAM filter
    if filters.get("min_vram"):
        where.append("gs.vram_gb >= %s")
        params.append(filters["min_vram"])

    # 💰 Price filters
    if filters.get("min_price"):
        where.append("x.price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("x.price <= %s")
        params.append(filters["max_price"])

    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      x.model_key AS gpu_model,
      gs.vram_gb,
      MIN(x.price) AS min_price,
      COUNT(DISTINCT x.store_id) AS offer_count,
      MAX(x.image_url) AS image_url
    FROM (
      SELECT
        TRIM(
          CASE
            -- ✅ AMD GPUs
            WHEN REGEXP_SUBSTR(po.title_raw, 'RX [0-9]{{4}}( XT)?') IS NOT NULL
            THEN CONCAT(
              'Radeon ',
              REGEXP_SUBSTR(po.title_raw, 'RX [0-9]{{4}}( XT)?')
            )

            -- ✅ NVIDIA GPUs
            ELSE REGEXP_SUBSTR(
              po.title_raw,
              'RTX [0-9]{{4}}( Ti)?'
            )
          END
        ) AS model_key,
        po.price,
        po.image_url,
        po.store_id
      FROM product_offers po
      WHERE po.price IS NOT NULL
        AND po.currency = 'MKD'
    ) x
    JOIN gpu_specs gs
      ON UPPER(
           REPLACE(
             REPLACE(gs.gpu_model, 'GeForce ', ''),
             'NVIDIA ',
             ''
           )
         ) = UPPER(x.model_key)
    WHERE {" AND ".join(where)}
    GROUP BY
      x.model_key,
      gs.vram_gb
    ORDER BY min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))



def get_gpu_details(model_key: str, vram: int):
    specs = fetchall("""
        SELECT
          gpu_model,
          vram_gb,
          memory_type,
          pcie_version,
          length_mm,
          recommended_psu_w
        FROM gpu_specs
        WHERE
          UPPER(
            REPLACE(
              REPLACE(gpu_model, 'GeForce ', ''),
              'Radeon ',
              ''
            )
          ) = UPPER(%s)
          AND vram_gb = %s
    """, (
        model_key.replace("Radeon ", "").replace("GeForce ", ""),
        vram,
    ))

    if not specs:
        return None

    offers = fetchall(f"""
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
            CASE
              WHEN REGEXP_SUBSTR(po.title_raw, 'RX [0-9]{{4}}( XT| XTX)?') IS NOT NULL
              THEN CONCAT(
                'Radeon ',
                REGEXP_SUBSTR(po.title_raw, 'RX [0-9]{{4}}( XT| XTX)?')
              )
              ELSE REGEXP_SUBSTR(
                po.title_raw,
                'RTX [0-9]{{4}}( Ti| SUPER)?'
              )
            END AS model_key
          FROM product_offers po
          WHERE po.price IS NOT NULL
            AND po.currency = 'MKD'
        ) b
        JOIN stores s ON s.store_id = b.store_id
        WHERE UPPER(b.model_key) = UPPER(%s)
        ORDER BY b.price ASC
    """, (model_key,))

    return {
        "gpu_model": model_key,
        "vram_gb": vram,
        "specs": specs[0],
        "offers": offers,
    }



