"""
Build recommendation service.

Selects best-value components within a budget allocation per profile.
Returns Intel and AMD builds, scored by a profile-weighted heuristic.
Only considers in-stock offers so the recommendation is immediately actionable.
"""

from app.core.constants import (
    PSU_CPU_BASE_OVERHEAD_W,
    PSU_DEFAULT_GPU_REC_W,
    PSU_DEFAULT_TDP_W,
    PSU_OVERHEAD_FACTOR,
    STANDARD_PSU_SIZES,
)
from app.core.db import fetchall

# Allocations sum to exactly 1.0 per profile. PSU is excluded (to be added later).
PROFILE_ALLOCATIONS = {
    "esports": {"gpu": 0.38, "cpu": 0.28, "mb": 0.14, "ram": 0.11, "storage": 0.09},
    "aaa":     {"gpu": 0.48, "cpu": 0.22, "mb": 0.12, "ram": 0.10, "storage": 0.08},
    "school":  {"cpu": 0.32, "gpu": 0.21, "ram": 0.21, "mb": 0.11, "storage": 0.15},
}


# ─── Component selectors ─────────────────────────────────────────

def _select_cpu(max_price: float, brand: str) -> dict | None:
    rows = fetchall(
        """
        SELECT
          cs.product_id,
          cs.cpu_model,
          cs.cores,
          cs.socket,
          cs.memory_type,
          cs.tdp_w,
          MIN(po.price) AS min_price
        FROM cpu_specs cs
        JOIN products p  ON p.product_id = cs.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = cs.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
          AND cs.brand = %s
        GROUP BY cs.product_id, cs.cpu_model, cs.cores, cs.socket, cs.memory_type, cs.tdp_w
        ORDER BY COALESCE(cs.tdp_w, 0) DESC, cs.cores DESC, min_price ASC
        LIMIT 1
        """,
        (max_price, brand),
    )
    return rows[0] if rows else None


def _select_mb(max_price: float, cpu_socket: str, memory_type: str) -> dict | None:
    # Exact socket + memory_type match first
    rows = fetchall(
        """
        SELECT
          mb.product_id,
          mb.mb_model,
          mb.socket,
          mb.memory_type,
          MIN(po.price) AS min_price
        FROM mb_specs mb
        JOIN products p ON p.product_id = mb.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = mb.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
          AND mb.socket = %s
          AND mb.memory_type = %s
        GROUP BY mb.product_id, mb.mb_model, mb.socket, mb.memory_type
        ORDER BY min_price ASC
        LIMIT 1
        """,
        (max_price, cpu_socket, memory_type),
    )
    if rows:
        return rows[0]
    # Fallback: socket-only — caller must validate memory_type after
    rows = fetchall(
        """
        SELECT
          mb.product_id,
          mb.mb_model,
          mb.socket,
          mb.memory_type,
          MIN(po.price) AS min_price
        FROM mb_specs mb
        JOIN products p ON p.product_id = mb.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = mb.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
          AND mb.socket = %s
        GROUP BY mb.product_id, mb.mb_model, mb.socket, mb.memory_type
        ORDER BY min_price ASC
        LIMIT 1
        """,
        (max_price, cpu_socket),
    )
    return rows[0] if rows else None


def _select_ram(max_price: float, memory_type: str) -> dict | None:
    rows = fetchall(
        """
        SELECT
          r.product_id,
          r.series,
          r.brand,
          r.total_capacity_gb,
          r.sticks,
          r.memory_type,
          r.speed_mhz,
          MIN(po.price) AS min_price
        FROM ram_specs r
        JOIN products p ON p.product_id = r.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = r.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
          AND r.memory_type = %s
        GROUP BY r.product_id, r.series, r.brand, r.total_capacity_gb,
                 r.sticks, r.memory_type, r.speed_mhz
        ORDER BY r.sticks DESC, r.total_capacity_gb DESC, min_price ASC
        LIMIT 5
        """,
        (max_price, memory_type),
    )
    if not rows:
        return None
    for r in rows:
        if (r.get("sticks") or 1) >= 2:
            return r
    # Fallback: double a single stick
    best = dict(rows[0])
    best["sticks"] = 2
    best["min_price"] = best["min_price"] * 2
    best["total_capacity_gb"] = best["total_capacity_gb"] * 2
    return best


def _select_gpu(max_price: float) -> dict | None:
    # recommended_psu_w is a manufacturer proxy for GPU performance tier
    rows = fetchall(
        """
        SELECT
          gs.product_id,
          gs.gpu_model,
          gs.vram_gb,
          gs.recommended_psu_w,
          MIN(po.price) AS min_price
        FROM gpu_specs gs
        JOIN products p ON p.product_id = gs.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = gs.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
        GROUP BY gs.product_id, gs.gpu_model, gs.vram_gb, gs.recommended_psu_w
        ORDER BY COALESCE(gs.recommended_psu_w, 0) DESC, gs.vram_gb DESC, min_price ASC
        LIMIT 1
        """,
        (max_price,),
    )
    return rows[0] if rows else None


def _select_storage(max_price: float, prefer_nvme: bool = True) -> dict | None:
    if prefer_nvme:
        order = "ORDER BY (CASE WHEN s.type = 'NVMe' THEN 0 ELSE 1 END), s.capacity_gb DESC, min_price ASC"
    else:
        order = "ORDER BY s.capacity_gb DESC, min_price ASC"
    rows = fetchall(
        f"""
        SELECT
          s.product_id,
          s.series,
          s.brand,
          s.capacity_gb,
          s.type,
          s.interface,
          MIN(po.price) AS min_price
        FROM storage_specs s
        JOIN products p ON p.product_id = s.product_id AND p.spec_status = 'ok'
        JOIN product_offers po ON po.product_id = s.product_id
        WHERE po.price IS NOT NULL
          AND po.in_stock = 1
          AND po.price <= %s
        GROUP BY s.product_id, s.series, s.brand, s.capacity_gb, s.type, s.interface
        {order}
        LIMIT 1
        """,
        (max_price,),
    )
    return rows[0] if rows else None


def _calc_psu(cpu: dict, gpu: dict) -> int | None:
    cpu_tdp = cpu.get("tdp_w") or PSU_DEFAULT_TDP_W
    gpu_rec = gpu.get("recommended_psu_w") or PSU_DEFAULT_GPU_REC_W
    estimated = int((cpu_tdp + PSU_CPU_BASE_OVERHEAD_W) * PSU_OVERHEAD_FACTOR)
    needed = max(estimated, gpu_rec)
    for size in STANDARD_PSU_SIZES:
        if needed <= size:
            return size
    return STANDARD_PSU_SIZES[-1]


def _compute_min_budget(allocation: dict, brand: str) -> int:
    """
    Query the cheapest in-stock price per component and compute the minimum total
    budget at which every allocation slice can afford its cheapest part.
    """
    def _floor(query, params=()):
        rows = fetchall(query, params)
        v = rows[0]["floor"] if rows else None
        return float(v) if v else None

    floors = {
        "cpu": _floor(
            """
            SELECT MIN(po.price) AS floor FROM cpu_specs cs
            JOIN products p ON p.product_id = cs.product_id AND p.spec_status = 'ok'
            JOIN product_offers po ON po.product_id = cs.product_id
            WHERE po.in_stock = 1 AND po.price IS NOT NULL AND cs.brand = %s
            """,
            (brand,),
        ),
        "gpu": _floor(
            """
            SELECT MIN(po.price) AS floor FROM gpu_specs gs
            JOIN products p ON p.product_id = gs.product_id AND p.spec_status = 'ok'
            JOIN product_offers po ON po.product_id = gs.product_id
            WHERE po.in_stock = 1 AND po.price IS NOT NULL
            """,
        ),
        "mb": _floor(
            """
            SELECT MIN(po.price) AS floor FROM mb_specs mb
            JOIN products p ON p.product_id = mb.product_id AND p.spec_status = 'ok'
            JOIN product_offers po ON po.product_id = mb.product_id
            WHERE po.in_stock = 1 AND po.price IS NOT NULL
            """,
        ),
        "ram": _floor(
            """
            SELECT MIN(po.price) AS floor FROM ram_specs r
            JOIN products p ON p.product_id = r.product_id AND p.spec_status = 'ok'
            JOIN product_offers po ON po.product_id = r.product_id
            WHERE po.in_stock = 1 AND po.price IS NOT NULL
            """,
        ),
        "storage": _floor(
            """
            SELECT MIN(po.price) AS floor FROM storage_specs s
            JOIN products p ON p.product_id = s.product_id AND p.spec_status = 'ok'
            JOIN product_offers po ON po.product_id = s.product_id
            WHERE po.in_stock = 1 AND po.price IS NOT NULL
            """,
        ),
    }

    min_total = 0.0
    for part, floor in floors.items():
        ratio = allocation.get(part, 0)
        if floor and ratio:
            # budget_slice = total * ratio must be >= floor → total >= floor / ratio
            min_total = max(min_total, floor / ratio)

    return int(min_total * 1.10)  # 10% headroom


def _value_score(build: dict, total: float, profile: str) -> float:
    if not total or total <= 0:
        return 0.0
    cpu     = build.get("cpu") or {}
    gpu     = build.get("gpu") or {}
    ram     = build.get("ram") or {}
    storage = build.get("storage") or {}

    cores      = float(cpu.get("cores") or 0)
    gpu_power  = float(gpu.get("recommended_psu_w") or 0) / 100.0  # normalize to ~5–10 range
    vram       = float(gpu.get("vram_gb") or 0)
    ram_gb     = float(ram.get("total_capacity_gb") or 0)
    storage_sc = float(storage.get("capacity_gb") or 0) / 512.0
    is_nvme    = 1.0 if (storage.get("type") == "NVMe") else 0.0

    if profile == "aaa":
        raw = gpu_power * 3.0 + vram * 2.0 + cores * 1.2 + ram_gb * 0.6 + storage_sc * 0.4 + is_nvme * 2.0
    elif profile == "school":
        raw = cores * 2.0 + ram_gb * 1.2 + vram * 0.8 + storage_sc * 0.8 + is_nvme * 1.0
    else:  # esports
        raw = gpu_power * 2.0 + vram * 1.5 + cores * 1.5 + ram_gb * 0.7 + storage_sc * 0.4 + is_nvme * 1.5

    return round(raw / total, 6)


def _build_for_brand(budgets: dict, profile: str, brand: str) -> dict | None:
    prefer_nvme = profile in ("esports", "aaa")

    cpu = _select_cpu(budgets["cpu"], brand)
    if not cpu:
        return None

    cpu_socket = cpu["socket"]
    cpu_mem    = cpu.get("memory_type") or "DDR4"

    mb = _select_mb(budgets["mb"], cpu_socket, cpu_mem)
    if not mb:
        return None

    # Hard compatibility gates — both must agree
    if mb["socket"] != cpu_socket:
        return None
    mb_mem = mb.get("memory_type") or cpu_mem
    if mb_mem and mb_mem != cpu_mem:
        return None

    # RAM must match the actual memory type the MB exposes
    ram     = _select_ram(budgets["ram"], mb_mem)
    gpu     = _select_gpu(budgets["gpu"])
    storage = _select_storage(budgets["storage"], prefer_nvme=prefer_nvme)

    psu_w = _calc_psu(cpu, gpu) if gpu else None

    build = {
        "cpu":               cpu,
        "mb":                mb,
        "ram":               ram,
        "gpu":               gpu,
        "storage":           storage,
        "recommended_psu_w": psu_w,
    }

    total = sum(
        float(part["min_price"])
        for part in build.values()
        if isinstance(part, dict) and part.get("min_price")
    )

    return {
        "brand":       brand,
        "build":       build,
        "total_price": round(total, 2),
        "value_score": _value_score(build, total, profile),
    }


def recommend_build(budget: int, profile: str) -> dict:
    if profile not in PROFILE_ALLOCATIONS:
        raise ValueError(f"profile must be one of {list(PROFILE_ALLOCATIONS)}")

    allocation = PROFILE_ALLOCATIONS[profile]
    budgets    = {part: budget * ratio for part, ratio in allocation.items()}

    intel = _build_for_brand(budgets, profile, "Intel")
    amd   = _build_for_brand(budgets, profile, "AMD")

    if not intel and not amd:
        intel_min = _compute_min_budget(allocation, "Intel")
        amd_min   = _compute_min_budget(allocation, "AMD")
        return {
            "budget":         budget,
            "profile":        profile,
            "intel":          None,
            "amd":            None,
            "winner":         None,
            "error":          "budget_too_low",
            "minimum_budget": min(intel_min, amd_min),
        }

    if intel and amd:
        winner = "intel" if intel["value_score"] >= amd["value_score"] else "amd"
    elif intel:
        winner = "intel"
    else:
        winner = "amd"

    return {
        "budget":  budget,
        "profile": profile,
        "intel":   intel,
        "amd":     amd,
        "winner":  winner,
    }
