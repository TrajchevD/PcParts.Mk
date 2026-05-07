# app/services/recommendation_service.py

from app.db import fetchall

PROFILE_ALLOCATIONS = {
    "esports": {"gpu": 0.35, "cpu": 0.25, "ram": 0.10, "storage": 0.08, "motherboard": 0.12},
    "aaa":     {"gpu": 0.45, "cpu": 0.20, "ram": 0.10, "storage": 0.08, "motherboard": 0.10},
    "school":  {"cpu": 0.30, "gpu": 0.20, "ram": 0.20, "storage": 0.15, "motherboard": 0.10},
}

STANDARD_PSU_SIZES = [450, 550, 650, 750, 850, 1000]


# ---------------------------
# Selectors (REAL schema)
# ---------------------------

def _select_gpu(max_price: int):
    return fetchall("""
        SELECT
            g.product_id,
            g.gpu_model,
            g.vram_gb,
            MIN(po.price) AS min_price
        FROM gpu_specs g
        JOIN product_offers po ON po.product_id = g.product_id
        WHERE po.price IS NOT NULL
          AND po.currency = 'MKD'
          AND po.price <= %s
        GROUP BY g.product_id, g.gpu_model, g.vram_gb
        ORDER BY g.vram_gb DESC, min_price ASC
        LIMIT 1
    """, (max_price,))


def _select_cpu_by_brand(max_price: int, brand: str):
    """
    Tries 2 approaches:
    A) cpu_specs.brand exists
    B) fallback by cpu_model string contains 'Intel' or 'Ryzen'
    """
    # A) If you have c.brand column
    rows = fetchall("""
        SELECT
            c.product_id,
            c.cpu_model,
            c.cores,
            MIN(po.price) AS min_price
        FROM cpu_specs c
        JOIN product_offers po ON po.product_id = c.product_id
        WHERE po.price IS NOT NULL
          AND po.currency = 'MKD'
          AND po.price <= %s
          AND (c.brand = %s OR c.brand IS NULL)
        GROUP BY c.product_id, c.cpu_model, c.cores
        ORDER BY c.cores DESC, min_price ASC
        LIMIT 20
    """, (max_price, brand))

    # Filter in Python in case c.brand is NULL / not reliable
    if brand.lower() == "intel":
        rows = [r for r in rows if "intel" in (r["cpu_model"] or "").lower() or "core" in (r["cpu_model"] or "").lower()]
    else:
        rows = [r for r in rows if "ryzen" in (r["cpu_model"] or "").lower() or "amd" in (r["cpu_model"] or "").lower()]

    return rows[:1]


def _select_motherboard(max_price: int, cpu_socket: str):
    return fetchall("""
        SELECT
            m.product_id,
            m.model,
            m.socket,
            m.memory_type,
            MIN(po.price) AS min_price
        FROM mb_specs_v2 m
        JOIN product_offers po ON po.product_id = m.product_id
        WHERE po.price IS NOT NULL
          AND po.currency = 'MKD'
          AND po.price <= %s
          AND m.socket = %s
        GROUP BY m.product_id, m.model, m.socket, m.memory_type
        ORDER BY min_price ASC
        LIMIT 1
    """, (max_price, cpu_socket))


def _select_ram(max_price: int, memory_type: str):

    rows = fetchall("""
        SELECT
            r.product_id,
            r.model,
            r.total_capacity_gb,
            r.kit_modules,
            r.memory_type,
            MIN(po.price) AS min_price
        FROM ram_specs_v2 r
        JOIN product_offers po ON po.product_id = r.product_id
        WHERE po.price IS NOT NULL
          AND po.currency = 'MKD'
          AND po.price <= %s
          AND r.memory_type = %s
        GROUP BY r.product_id, r.model, r.total_capacity_gb, r.kit_modules, r.memory_type
        ORDER BY 
            r.kit_modules DESC,
            r.total_capacity_gb DESC,
            min_price ASC
        LIMIT 5
    """, (max_price, memory_type))

    if not rows:
        return None

    # Prefer kit
    for r in rows:
        if (r.get("kit_modules") or 1) >= 2:
            r["quantity"] = 1
            return r

    # Fallback → duplicate single stick
    best = rows[0]
    best["quantity"] = 2
    best["min_price"] = best["min_price"] * 2
    best["total_capacity_gb"] = best["total_capacity_gb"] * 2
    return best


def _select_storage(max_price: int):
    return fetchall("""
        SELECT
            s.product_id,
            s.model,
            s.capacity_gb,
            MIN(po.price) AS min_price
        FROM storage_specs_v2 s
        JOIN product_offers po ON po.product_id = s.product_id
        WHERE po.price IS NOT NULL
          AND po.currency = 'MKD'
          AND po.price <= %s
        GROUP BY s.product_id, s.model, s.capacity_gb
        ORDER BY s.capacity_gb DESC, min_price ASC
        LIMIT 1
    """, (max_price,))


def _get_cpu_socket(product_id: int) -> str | None:
    rows = fetchall("SELECT socket FROM cpu_specs WHERE product_id = %s", (product_id,))
    return rows[0]["socket"] if rows else None


def _calculate_psu_wattage(cpu_product_id: int, gpu_product_id: int):
    cpu_rows = fetchall("SELECT tdp_w FROM cpu_specs WHERE product_id = %s", (cpu_product_id,))
    gpu_rows = fetchall("SELECT recommended_psu_w FROM gpu_specs WHERE product_id = %s", (gpu_product_id,))

    if not cpu_rows or not gpu_rows:
        return None

    cpu_tdp = cpu_rows[0].get("tdp_w") or 65
    gpu_rec = gpu_rows[0].get("recommended_psu_w") or 500

    # Simple model: (CPU + baseline) * safety, and never below GPU recommended
    estimated = int((cpu_tdp + 120) * 1.30)  # 120W = other components + approx GPU spikes
    needed = max(estimated, int(gpu_rec))

    for size in STANDARD_PSU_SIZES:
        if needed <= size:
            return size
    return 1000


# ---------------------------
# Value Score (heuristic)
# ---------------------------

def _value_score(build: dict, total_price: int, profile: str) -> float:
    """
    Student-friendly heuristic score:
    score = (weighted_specs_sum) / total_price

    Weights depend on profile (esports/aaa/school).
    """
    if not total_price or total_price <= 0:
        return 0.0

    cpu = build.get("cpu") or {}
    gpu = build.get("gpu") or {}
    ram = build.get("ram") or {}
    storage = build.get("storage") or {}

    cores = cpu.get("cores") or 0
    vram = gpu.get("vram_gb") or 0
    ram_gb = ram.get("total_capacity_gb") or 0
    storage_gb = storage.get("capacity_gb") or 0

    # normalize storage to TB-ish scale
    storage_score = storage_gb / 512.0  # 512GB ~ 1 point

    if profile == "aaa":
        # AAA: GPU heavy
        raw = (vram * 3.0) + (cores * 1.2) + (ram_gb * 0.6) + (storage_score * 0.4)
    elif profile == "school":
        # school: CPU/RAM heavy
        raw = (cores * 2.0) + (ram_gb * 1.2) + (vram * 0.8) + (storage_score * 0.8)
    else:
        # esports: balanced but CPU matters
        raw = (cores * 2.0) + (vram * 1.5) + (ram_gb * 0.7) + (storage_score * 0.4)

    return round(raw / float(total_price), 6)


# ---------------------------
# Build generator (brand)
# ---------------------------

def _build_for_brand(budgets: dict, profile: str, brand: str):
    cpu_rows = _select_cpu_by_brand(budgets["cpu"], brand)
    if not cpu_rows:
        return None

    cpu = cpu_rows[0]
    cpu_socket = _get_cpu_socket(cpu["product_id"])
    if not cpu_socket:
        return None

    mb_rows = _select_motherboard(budgets["motherboard"], cpu_socket)
    if not mb_rows:
        return None
    motherboard = mb_rows[0]
    memory_type = motherboard.get("memory_type")

    ram = _select_ram(budgets["ram"], memory_type)

    gpu_rows = _select_gpu(budgets["gpu"])
    gpu = gpu_rows[0] if gpu_rows else None

    storage_rows = _select_storage(budgets["storage"])
    storage = storage_rows[0] if storage_rows else None

    psu_w = None
    if cpu and gpu:
        psu_w = _calculate_psu_wattage(cpu["product_id"], gpu["product_id"])

    build = {
        "cpu": cpu,
        "motherboard": motherboard,
        "ram": ram,
        "gpu": gpu,
        "storage": storage,
        "recommended_psu_w": psu_w,
    }

    total_price = sum(
        part["min_price"]
        for part in build.values()
        if isinstance(part, dict) and "min_price" in part
    )

    score = _value_score(build, total_price, profile)

    return {
        "brand": brand,
        "build": build,
        "total_price": total_price,
        "value_score": score,
    }


def recommend_build(budget: int, profile: str):
    if profile not in PROFILE_ALLOCATIONS:
        raise ValueError("Invalid profile")

    allocation = PROFILE_ALLOCATIONS[profile]
    budgets = {part: int(budget * ratio) for part, ratio in allocation.items()}

    intel = _build_for_brand(budgets, profile, "Intel")
    amd = _build_for_brand(budgets, profile, "AMD")

    # Decide winner by value_score (if both exist)
    winner = None
    if intel and amd:
        winner = "intel" if intel["value_score"] >= amd["value_score"] else "amd"
    elif intel:
        winner = "intel"
    elif amd:
        winner = "amd"

    return {
        "budget": budget,
        "profile": profile,
        "intel": intel,
        "amd": amd,
        "winner": winner
    }