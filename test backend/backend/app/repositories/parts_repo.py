from app.db import fetchall

CPU_CATEGORY_ID = 4
MB_CATEGORY_ID = 1
RAM_CATEGORY_ID = 3
GPU_CATEGORY_ID = 2
STORAGE_CATEGORY_ID = 5

def search_cpus(search, socket, filters, sort, limit, offset):
    filters = filters or {}

    params = []
    where = ["p.category_id = %s"]
    params.append(CPU_CATEGORY_ID)

    if search:
        where.append("p.canonical_title LIKE %s")
        params.append(f"%{search}%")

    if socket:
        where.append("cs.socket = %s")
        params.append(socket)

    # ✅ FILTERS MUST BE HERE (before SQL)
    if filters.get("cores"):
        where.append("cs.cores >= %s")
        params.append(filters["cores"])

    order = "ASC"
    if sort == "price_desc":
        order = "DESC"

    if filters.get("min_price"):
        where.append("o.min_price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("o.min_price <= %s")
        params.append(filters["max_price"])

    # ✅ NOW build SQL
    sql = f"""
    SELECT
      p.product_id,
      p.canonical_title AS title,
      cs.socket,
      cs.cores,
      cs.threads,
      cs.base_clock_ghz,
      cs.boost_clock_ghz,
      cs.tdp_w,
      o.min_price,
      o.image_url
    FROM products p
    JOIN cpu_specs cs ON cs.product_id = p.product_id
    LEFT JOIN (
      SELECT po.product_id,
             po.price AS min_price,
             po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, MIN(price) AS min_price
        FROM product_offers
        WHERE price IS NOT NULL
        GROUP BY product_id
      ) m
        ON m.product_id = po.product_id
       AND m.min_price = po.price
    ) o ON o.product_id = p.product_id
    WHERE {" AND ".join(where)}
    ORDER BY o.min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]

    return fetchall(sql, tuple(params))



def search_mbs(search, socket, memory_type, filters, sort, limit, offset):
    params = [MB_CATEGORY_ID]
    where = ["p.category_id = %s"]

    if search:
        where.append("p.canonical_title LIKE %s")
        params.append(f"%{search}%")

    if socket:
        where.append("mb.socket = %s")
        params.append(socket)
    elif filters.get("socket"):
        where.append("mb.socket = %s")
        params.append(filters["socket"])

    if memory_type:
        where.append("mb.memory_type = %s")
        params.append(memory_type)
    
    if filters.get("form_factor"):
        where.append("mb.form_factor = %s")
        params.append(filters["form_factor"])

    if filters.get("memory_slots"):
        where.append("mb.memory_slots >= %s")
        params.append(filters["memory_slots"])

    if filters.get("min_price"):
        where.append("o.min_price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("o.min_price <= %s")
        params.append(filters["max_price"])

    order = "ASC"
    if sort == "price_desc":
        order = "DESC"

    sql = f"""
    SELECT
      p.product_id,
      p.canonical_title,
      mb.mb_model AS title,
      mb.socket,
      mb.memory_type,
      mb.memory_slots,
      mb.form_factor,
      mb.pcie_version,
      o.min_price,
      o.image_url
    FROM products p
    JOIN mb_specs mb ON mb.product_id = p.product_id
    LEFT JOIN (
      SELECT po.product_id,
             po.price AS min_price,
             po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, MIN(price) AS min_price
        FROM product_offers
        WHERE price IS NOT NULL
        GROUP BY product_id
      ) m ON m.product_id = po.product_id
         AND m.min_price = po.price
    ) o ON o.product_id = p.product_id
    WHERE {" AND ".join(where)}
    ORDER BY o.min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))

def search_ram(search, memory_type, filters, sort, limit, offset):
    filters = filters or {}
    params = [RAM_CATEGORY_ID]
    where = ["p.category_id = %s"]

    if search:
        where.append("p.canonical_title LIKE %s")
        params.append(f"%{search}%")

    if memory_type:
        where.append("r.memory_type = %s")  # ✅ FIX
        params.append(memory_type)

    if filters.get("capacity_gb"):
        where.append("r.total_capacity_gb >= %s")  # ✅ FIX
        params.append(filters["capacity_gb"])

    if filters.get("min_price"):
        where.append("o.min_price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("o.min_price <= %s")
        params.append(filters["max_price"])

    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      p.product_id,
      p.canonical_title AS title,
      r.memory_type,
      r.total_capacity_gb,
      r.sticks,
      r.capacity_per_stick_gb,
      r.speed_mhz,
      r.cas_latency,
      r.expo,
      r.xmp,
      o.min_price,
      o.image_url
    FROM products p
    JOIN ram_specs r ON r.product_id = p.product_id
    LEFT JOIN (
      SELECT po.product_id,
             po.price AS min_price,
             po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, MIN(price) AS min_price
        FROM product_offers
        WHERE price IS NOT NULL
        GROUP BY product_id
      ) m ON m.product_id = po.product_id
         AND m.min_price = po.price
    ) o ON o.product_id = p.product_id
    WHERE {" AND ".join(where)}
    ORDER BY o.min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))



def search_gpus(search, filters, sort, limit, offset):
    filters = filters or {}
    params = [GPU_CATEGORY_ID]
    where = ["p.category_id = %s"]

    if search:
        where.append("p.canonical_title LIKE %s")
        params.append(f"%{search}%")

    if filters.get("vram_gb"):
        where.append("g.vram_gb >= %s")  # ✅ FIX
        params.append(filters["vram_gb"])

    if filters.get("min_price"):
        where.append("o.min_price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("o.min_price <= %s")
        params.append(filters["max_price"])

    order = "ASC" if sort != "price_desc" else "DESC"

    sql = f"""
    SELECT
      p.product_id,
      p.canonical_title ,
      g.gpu_model AS title,
      g.vram_gb,
      g.memory_type,
      g.pcie_version,
      g.length_mm,
      g.recommended_psu_w,
      o.min_price,
      o.image_url
    FROM products p
    JOIN gpu_specs g ON g.product_id = p.product_id
    LEFT JOIN (
      SELECT po.product_id,
             po.price AS min_price,
             po.image_url
      FROM product_offers po
      JOIN (
        SELECT product_id, MIN(price) AS min_price
        FROM product_offers
        WHERE price IS NOT NULL
        GROUP BY product_id
      ) m ON m.product_id = po.product_id
         AND m.min_price = po.price
    ) o ON o.product_id = p.product_id
    WHERE {" AND ".join(where)}
    ORDER BY o.min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))


def search_storage(search, filters, sort, limit, offset):
    filters = filters or {}
    params = [STORAGE_CATEGORY_ID]
    where = ["p.category_id = %s"]

    if search:
        where.append("p.canonical_title LIKE %s")
        params.append(f"%{search}%")

    if filters.get("capacity_gb"):
        where.append("s.capacity_gb >= %s")  # ✅ FIX
        params.append(filters["capacity_gb"])

    if filters.get("interface"):
        where.append("s.interface = %s")  # ✅ FIX
        params.append(filters["interface"])

    if filters.get("min_price"):
        where.append("o.min_price >= %s")
        params.append(filters["min_price"])

    if filters.get("max_price"):
        where.append("o.min_price <= %s")
        params.append(filters["max_price"])

    order = "ASC" if sort != "price_desc" else "DESC"

    if sort == "price_desc":
        order = "DESC"
    sql = f"""
    SELECT
        p.product_id,
        p.canonical_title AS title,
        s.capacity_gb,
        s.interface,
        s.type AS storage_type,
        o.min_price,
        o.image_url
    FROM products p
    JOIN storage_specs s ON s.product_id = p.product_id
    LEFT JOIN (
        SELECT po.product_id,
               po.price AS min_price,
               po.image_url
        FROM product_offers po
        JOIN (
            SELECT product_id, MIN(price) AS min_price
            FROM product_offers
            WHERE price IS NOT NULL
            GROUP BY product_id
        ) m ON m.product_id = po.product_id
           AND m.min_price = po.price
    ) o ON o.product_id = p.product_id
    WHERE {" AND ".join(where)}
    ORDER BY o.min_price {order}
    LIMIT %s OFFSET %s
    """

    params += [limit, offset]
    return fetchall(sql, tuple(params))



def get_product(product_id: int):
    rows = fetchall(
        "SELECT product_id, category_id, title FROM products WHERE product_id=%s",
        (product_id,)
    )
    return rows[0] if rows else None