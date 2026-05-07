"""
Parts repository — all component search/detail queries.

Design notes:
- All listing and detail queries JOIN product_offers directly so MIN(price) and
  COUNT(DISTINCT store_id) reflect every store, not just the cheapest one.
- CPU/GPU grouped listings also apply an outlier filter (price >= avg * 0.7) to
  exclude mislabelled bundle offers, mirroring the old backend's guard.
- v_cheapest_offers is only used by the builder picker (search_cpus/gpus) where
  one row per product with its single best price is the desired result.
- spec_status = 'ok' filter on every spec JOIN ensures only enriched products appear.
- Price range filters use HAVING (not WHERE) because they reference aggregate functions;
  putting MIN() inside WHERE causes MySQL error 1111.
- Category filtering comes implicitly from the spec table JOIN; no hardcoded IDs needed.
"""

from app.core.db import fetchall, fetchone

# ─── helpers ─────────────────────────────────────────────────────────────────

def _order(sort: str) -> str:
    return "DESC" if sort == "price_desc" else "ASC"


def _escape_like(value: str) -> str:
    """Escape MySQL LIKE wildcards so user-provided text is treated as literals."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# ═══════════════════════════════════════════════════════════════════
# CPU
# ═══════════════════════════════════════════════════════════════════

def search_cpus(
    search: str | None,
    socket: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    """Builder options search: individual products with per-product offer count."""
    filters = filters or {}
    where, params = [], []

    if search:
        where.append("cs.cpu_model LIKE %s ESCAPE '\\\\'")
        params.append(f"%{_escape_like(search)}%")
    if socket:
        where.append("cs.socket = %s")
        params.append(socket)
    if filters.get("brand"):
        where.append("cs.brand = %s")
        params.append(filters["brand"])
    if filters.get("socket"):
        where.append("cs.socket = %s")
        params.append(filters["socket"])
    if filters.get("cores"):
        where.append("cs.cores >= %s")
        params.append(filters["cores"])
    if filters.get("min_price"):
        where.append("co.price >= %s")
        params.append(filters["min_price"])
    if filters.get("max_price"):
        where.append("co.price <= %s")
        params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""

    sql = f"""
    SELECT
      p.product_id,
      cs.cpu_model,
      cs.brand,
      cs.socket,
      cs.cores,
      cs.threads,
      cs.base_clock_ghz,
      cs.boost_clock_ghz,
      cs.tdp_w,
      cs.memory_type,
      co.price       AS min_price,
      co.image_url,
      (SELECT COUNT(*)
       FROM product_offers po2
       WHERE po2.product_id = p.product_id
         AND po2.in_stock = 1
         AND po2.price IS NOT NULL) AS offer_count
    FROM cpu_specs cs
    JOIN products p ON p.product_id = cs.product_id AND p.spec_status = 'ok'
    LEFT JOIN v_cheapest_offers co ON co.product_id = p.product_id
    WHERE 1=1 {where_clause}
    ORDER BY co.price {_order(sort)}, cs.cores DESC
    LIMIT %s OFFSET %s
    """
    params += [limit, offset]
    return fetchall(sql, tuple(params))


def list_grouped_cpus(
    search: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    """Product-listing view: one row per cpu_model with best price."""
    filters = filters or {}
    where, params = [], []
    having, having_params = [], []

    if search:
        where.append("cs.cpu_model LIKE %s ESCAPE '\\\\'")
        params.append(f"%{_escape_like(search)}%")
    if filters.get("brand"):
        where.append("cs.brand = %s")
        params.append(filters["brand"])
    if filters.get("socket"):
        where.append("cs.socket = %s")
        params.append(filters["socket"])
    if filters.get("min_cores"):
        where.append("cs.cores >= %s")
        params.append(filters["min_cores"])
    # Price filters go in HAVING — they reference the MIN() aggregate
    if filters.get("min_price"):
        having.append("MIN(po.price) >= %s")
        having_params.append(filters["min_price"])
    if filters.get("max_price"):
        having.append("MIN(po.price) <= %s")
        having_params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""
    having_clause = ("HAVING " + " AND ".join(having)) if having else ""

    # Mirror the old backend's approach: start from product_offers so COUNT(store_id)
    # and MIN(price) cover every store carrying any variant of this model.
    # The outlier subquery (avg_po) filters offers priced below 70% of the model
    # average — same guard as the old backend uses to exclude mislabelled bundles.
    sql = f"""
    SELECT
      cs.cpu_model,
      MAX(cs.brand)            AS brand,
      MAX(cs.socket)           AS socket,
      MAX(cs.cores)            AS cores,
      MAX(cs.threads)          AS threads,
      MAX(cs.base_clock_ghz)   AS base_clock_ghz,
      MAX(cs.boost_clock_ghz)  AS boost_clock_ghz,
      MAX(cs.tdp_w)            AS tdp_w,
      MAX(cs.memory_type)      AS memory_type,
      MIN(po.price)               AS min_price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url)           AS image_url
    FROM cpu_specs cs
    JOIN products p ON p.product_id = cs.product_id AND p.spec_status = 'ok'
    JOIN (
      SELECT po.product_id, po.price, po.store_id, po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, AVG(price) AS avg_price
        FROM product_offers
        WHERE price IS NOT NULL AND in_stock = 1
        GROUP BY product_id
      ) avg_po ON avg_po.product_id = po.product_id
               AND po.price >= avg_po.avg_price * 0.7
      WHERE po.in_stock = 1 AND po.price IS NOT NULL
    ) po ON po.product_id = p.product_id
    WHERE 1=1 {where_clause}
    GROUP BY cs.cpu_model
    {having_clause}
    ORDER BY min_price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += having_params + [limit, offset]
    return fetchall(sql, tuple(params))


def get_cpu_details(cpu_model: str) -> dict | None:
    specs = fetchone(
        """
        SELECT cs.*
        FROM cpu_specs cs
        JOIN products p ON p.product_id = cs.product_id AND p.spec_status = 'ok'
        WHERE UPPER(cs.cpu_model) = UPPER(%s)
        LIMIT 1
        """,
        (cpu_model,),
    )
    if not specs:
        return None

    offers = fetchall(
        """
        SELECT
          po.offer_id,
          s.name  AS store_name,
          po.price,
          po.price_text,
          po.product_url,
          po.in_stock,
          po.image_url,
          po.last_seen_at
        FROM cpu_specs cs
        JOIN products p   ON p.product_id = cs.product_id
        JOIN product_offers po ON po.product_id = p.product_id
        JOIN (
          SELECT product_id, AVG(price) AS avg_price
          FROM product_offers
          WHERE price IS NOT NULL AND in_stock = 1
          GROUP BY product_id
        ) avg_po ON avg_po.product_id = po.product_id
                 AND po.price >= avg_po.avg_price * 0.7
        JOIN stores s ON s.store_id = po.store_id
        WHERE UPPER(cs.cpu_model) = UPPER(%s)
          AND po.price IS NOT NULL
          AND po.in_stock = 1
        ORDER BY po.price ASC
        """,
        (cpu_model,),
    )
    return {"cpu_model": cpu_model, "specs": specs, "offers": offers}


# ═══════════════════════════════════════════════════════════════════
# GPU
# ═══════════════════════════════════════════════════════════════════

def list_grouped_gpus(
    search: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    """Product-listing view: one row per gpu_model+vram with best price."""
    filters = filters or {}
    where, params = [], []
    having, having_params = [], []

    if search:
        where.append("gs.gpu_model LIKE %s ESCAPE '\\\\'")
        params.append(f"%{_escape_like(search)}%")
    if filters.get("brand") == "NVIDIA":
        where.append("(gs.gpu_model LIKE 'GeForce%' OR gs.gpu_model LIKE 'RTX%' OR gs.gpu_model LIKE 'GTX%')")
    elif filters.get("brand") == "AMD":
        where.append("(gs.gpu_model LIKE 'Radeon%' OR gs.gpu_model LIKE 'RX%')")
    if filters.get("min_vram"):
        where.append("gs.vram_gb >= %s")
        params.append(filters["min_vram"])
    # Price filters go in HAVING — they reference the MIN() aggregate
    if filters.get("min_price"):
        having.append("MIN(po.price) >= %s")
        having_params.append(filters["min_price"])
    if filters.get("max_price"):
        having.append("MIN(po.price) <= %s")
        having_params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""
    having_clause = ("HAVING " + " AND ".join(having)) if having else ""

    # Mirror the old backend's approach: start from product_offers so COUNT(store_id)
    # and MIN(price) cover every store carrying any variant of this model.
    # The outlier subquery (avg_po) filters offers priced below 70% of the model
    # average — same guard as the old backend uses to exclude mislabelled bundles.
    sql = f"""
    SELECT
      gs.gpu_model,
      MAX(gs.vram_gb)           AS vram_gb,
      MAX(gs.memory_type)       AS memory_type,
      MAX(gs.pcie_version)      AS pcie_version,
      MAX(gs.length_mm)         AS length_mm,
      MAX(gs.recommended_psu_w) AS recommended_psu_w,
      MIN(po.price)               AS min_price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url)           AS image_url
    FROM gpu_specs gs
    JOIN products p ON p.product_id = gs.product_id AND p.spec_status = 'ok'
    JOIN (
      SELECT po.product_id, po.price, po.store_id, po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, AVG(price) AS avg_price
        FROM product_offers
        WHERE price IS NOT NULL AND in_stock = 1
        GROUP BY product_id
      ) avg_po ON avg_po.product_id = po.product_id
               AND po.price >= avg_po.avg_price * 0.7
      WHERE po.in_stock = 1 AND po.price IS NOT NULL
    ) po ON po.product_id = p.product_id
    WHERE 1=1 {where_clause}
    GROUP BY gs.gpu_model
    {having_clause}
    ORDER BY min_price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += having_params + [limit, offset]
    return fetchall(sql, tuple(params))


def search_gpus(
    search: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    """Builder options search: individual products with per-product offer count."""
    filters = filters or {}
    where, params = [], []

    if search:
        where.append("gs.gpu_model LIKE %s ESCAPE '\\\\'")
        params.append(f"%{_escape_like(search)}%")
    if filters.get("vram_gb"):
        where.append("gs.vram_gb >= %s")
        params.append(filters["vram_gb"])
    if filters.get("min_price"):
        where.append("co.price >= %s")
        params.append(filters["min_price"])
    if filters.get("max_price"):
        where.append("co.price <= %s")
        params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""

    sql = f"""
    SELECT
      p.product_id,
      gs.gpu_model,
      gs.vram_gb,
      gs.memory_type,
      gs.pcie_version,
      gs.recommended_psu_w,
      co.price AS min_price,
      co.image_url,
      (SELECT COUNT(*)
       FROM product_offers po2
       WHERE po2.product_id = p.product_id
         AND po2.in_stock = 1
         AND po2.price IS NOT NULL) AS offer_count
    FROM gpu_specs gs
    JOIN products p ON p.product_id = gs.product_id AND p.spec_status = 'ok'
    LEFT JOIN v_cheapest_offers co ON co.product_id = p.product_id
    WHERE 1=1 {where_clause}
    ORDER BY co.price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += [limit, offset]
    return fetchall(sql, tuple(params))


def get_gpu_details(gpu_model: str) -> dict | None:
    specs = fetchone(
        """
        SELECT gs.*
        FROM gpu_specs gs
        JOIN products p ON p.product_id = gs.product_id AND p.spec_status = 'ok'
        WHERE UPPER(gs.gpu_model) = UPPER(%s)
        LIMIT 1
        """,
        (gpu_model,),
    )
    if not specs:
        return None

    offers = fetchall(
        """
        SELECT
          po.offer_id,
          s.name  AS store_name,
          po.price,
          po.price_text,
          po.product_url,
          po.in_stock,
          po.image_url,
          po.last_seen_at
        FROM gpu_specs gs
        JOIN products p  ON p.product_id = gs.product_id
        JOIN product_offers po ON po.product_id = p.product_id
        JOIN (
          SELECT product_id, AVG(price) AS avg_price
          FROM product_offers
          WHERE price IS NOT NULL AND in_stock = 1
          GROUP BY product_id
        ) avg_po ON avg_po.product_id = po.product_id
                 AND po.price >= avg_po.avg_price * 0.7
        JOIN stores s ON s.store_id = po.store_id
        WHERE UPPER(gs.gpu_model) = UPPER(%s)
          AND po.price IS NOT NULL
          AND po.in_stock = 1
        ORDER BY po.price ASC
        """,
        (gpu_model,),
    )
    return {"gpu_model": gpu_model, "specs": specs, "offers": offers}


# ═══════════════════════════════════════════════════════════════════
# MOTHERBOARD
# ═══════════════════════════════════════════════════════════════════

def search_mbs(
    search: str | None,
    socket: str | None,
    memory_type: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    filters = filters or {}
    where, params = [], []
    having, having_params = [], []

    if search:
        safe = _escape_like(search)
        where.append("(mb.mb_model LIKE %s ESCAPE '\\\\' OR p.canonical_title LIKE %s ESCAPE '\\\\')")
        params += [f"%{safe}%", f"%{safe}%"]
    if socket:
        where.append("mb.socket = %s")
        params.append(socket)
    elif filters.get("socket"):
        where.append("mb.socket = %s")
        params.append(filters["socket"])
    if memory_type:
        where.append("mb.memory_type = %s")
        params.append(memory_type)
    elif filters.get("memory_type"):
        where.append("mb.memory_type = %s")
        params.append(filters["memory_type"])
    if filters.get("form_factor"):
        where.append("mb.form_factor = %s")
        params.append(filters["form_factor"])
    if filters.get("chipset"):
        where.append("mb.chipset = %s")
        params.append(filters["chipset"])
    if filters.get("min_price"):
        having.append("MIN(po.price) >= %s")
        having_params.append(filters["min_price"])
    if filters.get("max_price"):
        having.append("MIN(po.price) <= %s")
        having_params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""
    having_clause = ("HAVING " + " AND ".join(having)) if having else ""

    sql = f"""
    SELECT
      p.product_id,
      mb.mb_model,
      mb.brand,
      mb.chipset,
      mb.socket,
      mb.memory_type,
      mb.memory_slots,
      mb.max_memory_gb,
      mb.form_factor,
      mb.pcie_version,
      MIN(po.price)               AS min_price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url)           AS image_url
    FROM mb_specs mb
    JOIN products p ON p.product_id = mb.product_id AND p.spec_status = 'ok'
    JOIN product_offers po ON po.product_id = p.product_id
                           AND po.in_stock = 1
                           AND po.price IS NOT NULL
    WHERE 1=1 {where_clause}
    GROUP BY
      p.product_id, mb.mb_model, mb.brand, mb.chipset, mb.socket,
      mb.memory_type, mb.memory_slots, mb.max_memory_gb, mb.form_factor, mb.pcie_version
    {having_clause}
    ORDER BY min_price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += having_params + [limit, offset]
    return fetchall(sql, tuple(params))


def get_mb_details(product_id: int) -> dict | None:
    specs = fetchone(
        """
        SELECT mb.*
        FROM mb_specs mb
        JOIN products p ON p.product_id = mb.product_id AND p.spec_status = 'ok'
        WHERE mb.product_id = %s
        """,
        (product_id,),
    )
    if not specs:
        return None

    offers = fetchall(
        """
        SELECT
          po.offer_id,
          s.name  AS store_name,
          po.price,
          po.price_text,
          po.product_url,
          po.in_stock,
          po.image_url
        FROM product_offers po
        JOIN stores s ON s.store_id = po.store_id
        WHERE po.product_id = %s
          AND po.price IS NOT NULL
          AND po.in_stock = 1
        ORDER BY po.price ASC
        """,
        (product_id,),
    )
    return {"product_id": product_id, "specs": specs, "offers": offers}


# ═══════════════════════════════════════════════════════════════════
# RAM
# ═══════════════════════════════════════════════════════════════════

def search_ram(
    search: str | None,
    memory_type: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    filters = filters or {}
    where, params = [], []
    having, having_params = [], []

    if search:
        safe = _escape_like(search)
        where.append("(r.series LIKE %s ESCAPE '\\\\' OR r.brand LIKE %s ESCAPE '\\\\' OR p.canonical_title LIKE %s ESCAPE '\\\\')")
        params += [f"%{safe}%", f"%{safe}%", f"%{safe}%"]
    if memory_type:
        where.append("r.memory_type = %s")
        params.append(memory_type)
    elif filters.get("memory_type"):
        where.append("r.memory_type = %s")
        params.append(filters["memory_type"])
    if filters.get("capacity_gb"):
        where.append("r.total_capacity_gb >= %s")
        params.append(filters["capacity_gb"])
    if filters.get("min_price"):
        having.append("MIN(po.price) >= %s")
        having_params.append(filters["min_price"])
    if filters.get("max_price"):
        having.append("MIN(po.price) <= %s")
        having_params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""
    having_clause = ("HAVING " + " AND ".join(having)) if having else ""

    sql = f"""
    SELECT
      p.product_id,
      r.brand,
      r.series,
      r.memory_type,
      r.total_capacity_gb,
      r.sticks,
      r.capacity_per_stick_gb,
      r.speed_mhz,
      r.cas_latency,
      r.expo,
      r.xmp,
      MIN(po.price)               AS min_price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url)           AS image_url
    FROM ram_specs r
    JOIN products p ON p.product_id = r.product_id AND p.spec_status = 'ok'
    JOIN product_offers po ON po.product_id = p.product_id
                           AND po.in_stock = 1
                           AND po.price IS NOT NULL
    WHERE 1=1 {where_clause}
    GROUP BY
      p.product_id, r.brand, r.series, r.memory_type, r.total_capacity_gb,
      r.sticks, r.capacity_per_stick_gb, r.speed_mhz, r.cas_latency, r.expo, r.xmp
    {having_clause}
    ORDER BY min_price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += having_params + [limit, offset]
    return fetchall(sql, tuple(params))


def get_ram_details(product_id: int) -> dict | None:
    specs = fetchone(
        """
        SELECT r.*
        FROM ram_specs r
        JOIN products p ON p.product_id = r.product_id AND p.spec_status = 'ok'
        WHERE r.product_id = %s
        """,
        (product_id,),
    )
    if not specs:
        return None

    offers = fetchall(
        """
        SELECT
          po.offer_id,
          s.name  AS store_name,
          po.price,
          po.price_text,
          po.product_url,
          po.in_stock,
          po.image_url
        FROM product_offers po
        JOIN stores s ON s.store_id = po.store_id
        WHERE po.product_id = %s
          AND po.price IS NOT NULL
          AND po.in_stock = 1
        ORDER BY po.price ASC
        """,
        (product_id,),
    )
    return {"product_id": product_id, "specs": specs, "offers": offers}


# ═══════════════════════════════════════════════════════════════════
# STORAGE
# ═══════════════════════════════════════════════════════════════════

def search_storage(
    search: str | None,
    filters: dict,
    sort: str,
    limit: int,
    offset: int,
) -> list[dict]:
    filters = filters or {}
    where, params = [], []
    having, having_params = [], []

    if search:
        safe = _escape_like(search)
        where.append("(s.series LIKE %s ESCAPE '\\\\' OR s.brand LIKE %s ESCAPE '\\\\' OR p.canonical_title LIKE %s ESCAPE '\\\\')")
        params += [f"%{safe}%", f"%{safe}%", f"%{safe}%"]
    if filters.get("type"):
        where.append("s.type = %s")
        params.append(filters["type"])
    if filters.get("interface"):
        where.append("s.interface = %s")
        params.append(filters["interface"])
    if filters.get("capacity_gb"):
        where.append("s.capacity_gb >= %s")
        params.append(filters["capacity_gb"])
    if filters.get("min_price"):
        having.append("MIN(po.price) >= %s")
        having_params.append(filters["min_price"])
    if filters.get("max_price"):
        having.append("MIN(po.price) <= %s")
        having_params.append(filters["max_price"])

    where_clause = ("AND " + " AND ".join(where)) if where else ""
    having_clause = ("HAVING " + " AND ".join(having)) if having else ""

    sql = f"""
    SELECT
      p.product_id,
      s.brand,
      s.series,
      s.type,
      s.capacity_gb,
      s.form_factor,
      s.interface,
      s.pcie_version,
      s.rpm,
      MIN(po.price)               AS min_price,
      COUNT(DISTINCT po.store_id) AS offer_count,
      MAX(po.image_url)           AS image_url
    FROM storage_specs s
    JOIN products p ON p.product_id = s.product_id AND p.spec_status = 'ok'
    JOIN product_offers po ON po.product_id = p.product_id
                           AND po.in_stock = 1
                           AND po.price IS NOT NULL
    WHERE 1=1 {where_clause}
    GROUP BY
      p.product_id, s.brand, s.series, s.type, s.capacity_gb,
      s.form_factor, s.interface, s.pcie_version, s.rpm
    {having_clause}
    ORDER BY min_price {_order(sort)}
    LIMIT %s OFFSET %s
    """
    params += having_params + [limit, offset]
    return fetchall(sql, tuple(params))


def get_storage_details(product_id: int) -> dict | None:
    specs = fetchone(
        """
        SELECT s.*
        FROM storage_specs s
        JOIN products p ON p.product_id = s.product_id AND p.spec_status = 'ok'
        WHERE s.product_id = %s
        """,
        (product_id,),
    )
    if not specs:
        return None

    offers = fetchall(
        """
        SELECT
          po.offer_id,
          s.name  AS store_name,
          po.price,
          po.price_text,
          po.product_url,
          po.in_stock,
          po.image_url
        FROM product_offers po
        JOIN stores s ON s.store_id = po.store_id
        WHERE po.product_id = %s
          AND po.price IS NOT NULL
          AND po.in_stock = 1
        ORDER BY po.price ASC
        """,
        (product_id,),
    )
    return {"product_id": product_id, "specs": specs, "offers": offers}


# ═══════════════════════════════════════════════════════════════════
# Spec lookups used by compat service
# ═══════════════════════════════════════════════════════════════════

def get_cpu_specs(product_id: int) -> dict | None:
    return fetchone(
        "SELECT socket, cores, threads, memory_type FROM cpu_specs WHERE product_id = %s",
        (product_id,),
    )


def get_mb_specs(product_id: int) -> dict | None:
    return fetchone(
        "SELECT socket, memory_type, memory_slots, max_memory_gb FROM mb_specs WHERE product_id = %s",
        (product_id,),
    )


def get_ram_specs(product_id: int) -> dict | None:
    return fetchone(
        "SELECT memory_type, total_capacity_gb FROM ram_specs WHERE product_id = %s",
        (product_id,),
    )


def get_gpu_specs(product_id: int) -> dict | None:
    return fetchone(
        "SELECT vram_gb, recommended_psu_w, pcie_version FROM gpu_specs WHERE product_id = %s",
        (product_id,),
    )
