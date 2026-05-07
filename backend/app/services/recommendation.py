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

PROFILE_ALLOCATIONS = {
    "esports": {"gpu": 0.35, "cpu": 0.25, "ram": 0.10, "storage": 0.08, "mb": 0.12},
    "aaa":     {"gpu": 0.45, "cpu": 0.20, "ram": 0.10, "storage": 0.08, "mb": 0.10},
    "school":  {"cpu": 0.30, "gpu": 0.20, "ram": 0.20, "storage": 0.15, "mb": 0.10},
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
        ORDER BY cs.cores DESC, min_price ASC
        LIMIT 1
        """,
        (max_price, brand),
    )
    return rows[0] if rows else None


def _select_mb(max_price: float, cpu_socket: str, memory_type: str) -> dict | None:
    # Try exact socket + memory_type match first
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
    # Fallback: socket-only (memory_type may be stored differently in DB)
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
    # Prefer kits (sticks >= 2)
    for r in rows:
        if (r.get("sticks") or 1) >= 2:
            return r
    # Fallback: duplicate single stick
    best = dict(rows[0])
    best["sticks"] = 2
    best["min_price"] = best["min_price"] * 2
    best["total_capacity_gb"] = best["total_capacity_gb"] * 2
    return best


def _select_gpu(max_price: float) -> dict | None:
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
        ORDER BY gs.vram_gb DESC, min_price ASC
        LIMIT 1
        """,
        (max_price,),
    )
    return rows[0] if rows else None


def _select_storage(max_price: float) -> dict | None:
    rows = fetchall(
        """
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
        ORDER BY s.capacity_gb DESC, min_price ASC
        LIMIT 1
        """,
        (max_price,),
    )
    return rows[0] if rows else None


def _calc_psu(cpu: dict, gpu: dict) -> int | None:
    cpu_tdp = (cpu.get("tdp_w") or PSU_DEFAULT_TDP_W)
    gpu_rec = (gpu.get("recommended_psu_w") or PSU_DEFAULT_GPU_REC_W)
    estimated = int((cpu_tdp + PSU_CPU_BASE_OVERHEAD_W) * PSU_OVERHEAD_FACTOR)
    needed = max(estimated, gpu_rec)
    for size in STANDARD_PSU_SIZES:
        if needed <= size:
            return size
    return STANDARD_PSU_SIZES[-1]


def _value_score(build: dict, total: float, profile: str) -> float:
    if not total or total <= 0:
        return 0.0
    cpu = build.get("cpu") or {}
    gpu = build.get("gpu") or {}
    ram = build.get("ram") or {}
    storage = build.get("storage") or {}

    cores      = float(cpu.get("cores") or 0)
    vram       = float(gpu.get("vram_gb") or 0)
    ram_gb     = float(ram.get("total_capacity_gb") or 0)
    storage_sc = float(storage.get("capacity_gb") or 0) / 512.0

    if profile == "aaa":
        raw = vram * 3.0 + cores * 1.2 + ram_gb * 0.6 + storage_sc * 0.4
    elif profile == "school":
        raw = cores * 2.0 + ram_gb * 1.2 + vram * 0.8 + storage_sc * 0.8
    else:  # esports
        raw = cores * 2.0 + vram * 1.5 + ram_gb * 0.7 + storage_sc * 0.4

    return round(raw / total, 6)


def _build_for_brand(budgets: dict, profile: str, brand: str) -> dict | None:
    cpu = _select_cpu(budgets["cpu"], brand)
    if not cpu:
        return None

    memory_type = cpu.get("memory_type") or "DDR4"
    mb = _select_mb(budgets["mb"], cpu["socket"], memory_type)

    ram     = _select_ram(budgets["ram"], memory_type)
    gpu     = _select_gpu(budgets["gpu"])
    storage = _select_storage(budgets["storage"])
    psu_w   = _calc_psu(cpu, gpu) if cpu and gpu else None

    build = {
        "cpu": cpu,
        "mb": mb,
        "ram": ram,
        "gpu": gpu,
        "storage": storage,
        "recommended_psu_w": psu_w,
    }

    total = sum(
        float(part["min_price"])
        for part in build.values()
        if isinstance(part, dict) and part.get("min_price")
    )

    return {
        "brand": brand,
        "build": build,
        "total_price": round(total, 2),
        "value_score": _value_score(build, total, profile),
    }


def recommend_build(budget: int, profile: str) -> dict:
    if profile not in PROFILE_ALLOCATIONS:
        raise ValueError(f"profile must be one of {list(PROFILE_ALLOCATIONS)}")

    allocation = PROFILE_ALLOCATIONS[profile]
    budgets = {part: int(budget * ratio) for part, ratio in allocation.items()}

    intel = _build_for_brand(budgets, profile, "Intel")
    amd   = _build_for_brand(budgets, profile, "AMD")

    if intel and amd:
        winner = "intel" if intel["value_score"] >= amd["value_score"] else "amd"
    elif intel:
        winner = "intel"
    elif amd:
        winner = "amd"
    else:
        winner = None

    return {
        "budget": budget,
        "profile": profile,
        "intel": intel,
        "amd": amd,
        "winner": winner,
    }
