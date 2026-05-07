"""
Product comparison service.

Returns spec cards for up to N products in the same category.
CPU and GPU are looked up by model name (string id).
MB, RAM, Storage are looked up by product_id (int).
"""

from app.core.db import fetchall

VALID_CATEGORIES = {"cpu", "gpu", "mb", "ram", "storage"}


def compare_products(category: str, ids: list) -> list[dict]:
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'")
    if not ids:
        return []

    placeholders = ",".join(["%s"] * len(ids))

    # ── CPU ──────────────────────────────────────────────────────
    if category == "cpu":
        rows = fetchall(
            f"""
            SELECT
              cs.cpu_model   AS id,
              cs.cpu_model   AS model,
              cs.brand,
              cs.socket,
              cs.cores,
              cs.threads,
              cs.base_clock_ghz  AS base_clock,
              cs.boost_clock_ghz AS boost_clock,
              cs.tdp_w           AS tdp,
              cs.memory_type,
              MAX(co.image_url)  AS image_url
            FROM cpu_specs cs
            JOIN products p ON p.product_id = cs.product_id
            LEFT JOIN v_cheapest_offers co ON co.product_id = p.product_id
            WHERE cs.cpu_model IN ({placeholders})
            GROUP BY
              cs.cpu_model, cs.brand, cs.socket, cs.cores, cs.threads,
              cs.base_clock_ghz, cs.boost_clock_ghz, cs.tdp_w, cs.memory_type
            ORDER BY FIELD(cs.cpu_model, {placeholders})
            """,
            tuple(ids) * 2,
        )
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "image_url": r["image_url"],
                "specs": {
                    "brand": r["brand"],
                    "socket": r["socket"],
                    "cores": r["cores"],
                    "threads": r["threads"],
                    "base_clock": r["base_clock"],
                    "boost_clock": r["boost_clock"],
                    "tdp": r["tdp"],
                    "memory_type": r["memory_type"],
                },
            }
            for r in rows
        ]

    # ── GPU ──────────────────────────────────────────────────────
    if category == "gpu":
        rows = fetchall(
            f"""
            SELECT
              gs.gpu_model         AS id,
              gs.gpu_model         AS model,
              gs.vram_gb,
              gs.memory_type,
              gs.pcie_version,
              gs.length_mm,
              gs.recommended_psu_w,
              MAX(co.image_url)    AS image_url
            FROM gpu_specs gs
            JOIN products p ON p.product_id = gs.product_id
            LEFT JOIN v_cheapest_offers co ON co.product_id = p.product_id
            WHERE gs.gpu_model IN ({placeholders})
            GROUP BY
              gs.gpu_model, gs.vram_gb, gs.memory_type,
              gs.pcie_version, gs.length_mm, gs.recommended_psu_w
            ORDER BY FIELD(gs.gpu_model, {placeholders})
            """,
            tuple(ids) * 2,
        )
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "image_url": r["image_url"],
                "specs": {
                    "vram_gb": r["vram_gb"],
                    "memory_type": r["memory_type"],
                    "pcie_version": r["pcie_version"],
                    "length_mm": r["length_mm"],
                    "recommended_psu_w": r["recommended_psu_w"],
                },
            }
            for r in rows
        ]

    # ── MB ───────────────────────────────────────────────────────
    if category == "mb":
        ids = [int(i) for i in ids]
        placeholders = ",".join(["%s"] * len(ids))
        rows = fetchall(
            f"""
            SELECT
              mb.product_id    AS id,
              mb.mb_model      AS model,
              mb.brand,
              mb.chipset,
              mb.socket,
              mb.memory_type,
              mb.memory_slots,
              mb.max_memory_gb,
              mb.form_factor,
              mb.pcie_version,
              MAX(co.image_url) AS image_url
            FROM mb_specs mb
            LEFT JOIN v_cheapest_offers co ON co.product_id = mb.product_id
            WHERE mb.product_id IN ({placeholders})
            GROUP BY
              mb.product_id, mb.mb_model, mb.brand, mb.chipset, mb.socket,
              mb.memory_type, mb.memory_slots, mb.max_memory_gb,
              mb.form_factor, mb.pcie_version
            ORDER BY FIELD(mb.product_id, {placeholders})
            """,
            tuple(ids) * 2,
        )
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "image_url": r["image_url"],
                "specs": {
                    "brand": r["brand"],
                    "chipset": r["chipset"],
                    "socket": r["socket"],
                    "memory_type": r["memory_type"],
                    "memory_slots": r["memory_slots"],
                    "max_memory_gb": r["max_memory_gb"],
                    "form_factor": r["form_factor"],
                    "pcie_version": r["pcie_version"],
                },
            }
            for r in rows
        ]

    # ── RAM ──────────────────────────────────────────────────────
    if category == "ram":
        ids = [int(i) for i in ids]
        placeholders = ",".join(["%s"] * len(ids))
        rows = fetchall(
            f"""
            SELECT
              r.product_id         AS id,
              r.series             AS model,
              r.brand,
              r.memory_type,
              r.total_capacity_gb,
              r.sticks,
              r.capacity_per_stick_gb,
              r.speed_mhz,
              r.cas_latency,
              r.expo,
              r.xmp,
              MAX(co.image_url)    AS image_url
            FROM ram_specs r
            LEFT JOIN v_cheapest_offers co ON co.product_id = r.product_id
            WHERE r.product_id IN ({placeholders})
            GROUP BY
              r.product_id, r.series, r.brand, r.memory_type,
              r.total_capacity_gb, r.sticks, r.capacity_per_stick_gb,
              r.speed_mhz, r.cas_latency, r.expo, r.xmp
            ORDER BY FIELD(r.product_id, {placeholders})
            """,
            tuple(ids) * 2,
        )
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "image_url": r["image_url"],
                "specs": {
                    "brand": r["brand"],
                    "memory_type": r["memory_type"],
                    "total_capacity_gb": r["total_capacity_gb"],
                    "sticks": r["sticks"],
                    "capacity_per_stick_gb": r["capacity_per_stick_gb"],
                    "speed_mhz": r["speed_mhz"],
                    "cas_latency": r["cas_latency"],
                    "expo": bool(r["expo"]),
                    "xmp": bool(r["xmp"]),
                },
            }
            for r in rows
        ]

    # ── Storage ──────────────────────────────────────────────────
    if category == "storage":
        ids = [int(i) for i in ids]
        placeholders = ",".join(["%s"] * len(ids))
        rows = fetchall(
            f"""
            SELECT
              s.product_id      AS id,
              s.series          AS model,
              s.brand,
              s.type,
              s.capacity_gb,
              s.interface,
              s.form_factor,
              s.pcie_version,
              s.rpm,
              MAX(co.image_url) AS image_url
            FROM storage_specs s
            LEFT JOIN v_cheapest_offers co ON co.product_id = s.product_id
            WHERE s.product_id IN ({placeholders})
            GROUP BY
              s.product_id, s.series, s.brand, s.type, s.capacity_gb,
              s.interface, s.form_factor, s.pcie_version, s.rpm
            ORDER BY FIELD(s.product_id, {placeholders})
            """,
            tuple(ids) * 2,
        )
        return [
            {
                "id": r["id"],
                "model": r["model"],
                "image_url": r["image_url"],
                "specs": {
                    "brand": r["brand"],
                    "type": r["type"],
                    "capacity_gb": r["capacity_gb"],
                    "interface": r["interface"],
                    "form_factor": r["form_factor"],
                    "pcie_version": r["pcie_version"],
                    "rpm": r["rpm"],
                },
            }
            for r in rows
        ]

    return []
