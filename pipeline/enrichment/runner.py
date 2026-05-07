import logging
import time

from db import fetchall, execute
from enrichment.choose_offer import pick_best_offer
from enrichment.parsers.cpu     import parse as parse_cpu
from enrichment.parsers.gpu     import parse as parse_gpu
from enrichment.parsers.mb      import parse as parse_mb
from enrichment.parsers.ram     import parse as parse_ram
from enrichment.parsers.storage import parse as parse_storage

log = logging.getLogger("pipeline.enrichment")

PARSERS = {
    "cpu":     parse_cpu,
    "gpu":     parse_gpu,
    "mb":      parse_mb,
    "ram":     parse_ram,
    "storage": parse_storage,
    "memory":  parse_storage,   # Neptun/Setec alias for storage
}

SPEC_TABLES = {
    "cpu": {
        "table":    "cpu_specs",
        "cols":     ["product_id", "cpu_model", "brand", "socket", "cores",
                     "threads", "base_clock_ghz", "boost_clock_ghz", "tdp_w", "memory_type"],
        "keys":     ["cpu_model", "brand", "socket", "cores", "threads",
                     "base_clock_ghz", "boost_clock_ghz", "tdp_w", "memory_type"],
        "required": ["socket"],
    },
    "gpu": {
        "table":    "gpu_specs",
        "cols":     ["product_id", "gpu_model", "vram_gb", "memory_type",
                     "pcie_version", "length_mm", "recommended_psu_w"],
        "keys":     ["gpu_model", "vram_gb", "memory_type", "pcie_version",
                     "length_mm", "recommended_psu_w"],
        "required": ["gpu_model", "vram_gb"],
    },
    "mb": {
        "table":    "mb_specs",
        "cols":     ["product_id", "mb_model", "brand", "chipset", "socket",
                     "form_factor", "memory_type", "memory_slots", "max_memory_gb", "pcie_version"],
        "keys":     ["mb_model", "brand", "chipset", "socket", "form_factor",
                     "memory_type", "memory_slots", "max_memory_gb", "pcie_version"],
        "required": ["socket", "memory_type"],
    },
    "ram": {
        "table":    "ram_specs",
        "cols":     ["product_id", "brand", "series", "memory_type", "total_capacity_gb",
                     "sticks", "capacity_per_stick_gb", "speed_mhz", "cas_latency",
                     "expo", "xmp", "ecc"],
        "keys":     ["brand", "series", "memory_type", "total_capacity_gb",
                     "sticks", "capacity_per_stick_gb", "speed_mhz", "cas_latency",
                     "expo", "xmp", "ecc"],
        "required": ["memory_type", "total_capacity_gb"],
    },
    "storage": {
        "table":    "storage_specs",
        "cols":     ["product_id", "type", "brand", "series", "capacity_gb",
                     "form_factor", "interface", "pcie_version", "rpm"],
        "keys":     ["type", "brand", "series", "capacity_gb",
                     "form_factor", "interface", "pcie_version", "rpm"],
        "required": ["type", "capacity_gb"],
    },
}
SPEC_TABLES["memory"] = SPEC_TABLES["storage"]


def _upsert_specs(cfg: dict, product_id: int, specs: dict) -> None:
    values       = [product_id] + [specs.get(k) for k in cfg["keys"]]
    col_str      = ", ".join(cfg["cols"])
    placeholders = ", ".join(["%s"] * len(cfg["cols"]))
    update_str   = ", ".join(f"{k}=VALUES({k})" for k in cfg["keys"])
    execute(
        f"INSERT INTO {cfg['table']} ({col_str}) VALUES ({placeholders})"
        f" ON DUPLICATE KEY UPDATE {update_str}",
        tuple(values),
    )


def _mark_status(product_id: int, status: str) -> None:
    execute("UPDATE products SET spec_status=%s WHERE product_id=%s", (status, product_id))


def run(limit: int = 300, include_failed: bool = False) -> dict:
    status_filter = "'pending', 'failed'" if include_failed else "'pending'"
    products = fetchall(
        f"""
        SELECT p.product_id, c.slug AS category, p.canonical_title
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE p.spec_status IN ({status_filter})
        ORDER BY p.product_id DESC
        LIMIT %s
        """,
        (limit,),
    )

    log.info(f"Enrichment: {len(products)} pending products")
    ok = skipped = failed = 0

    for p in products:
        pid    = p["product_id"]
        slug   = p["category"]
        cfg    = SPEC_TABLES.get(slug)
        parser = PARSERS.get(slug)

        if not cfg or not parser:
            skipped += 1
            continue

        offer = pick_best_offer(pid)
        if not offer:
            skipped += 1
            continue

        title = offer["title_raw"] or p["canonical_title"]
        url   = offer["product_url"] or ""

        try:
            specs = parser(title, url)
        except Exception as exc:
            log.warning(f"  pid={pid} parser error: {exc}")
            _mark_status(pid, "failed")
            failed += 1
            time.sleep(0.5)
            continue

        if not specs or not all(specs.get(k) is not None for k in cfg["required"]):
            log.debug(f"  pid={pid} [{slug}] missing required fields")
            _mark_status(pid, "failed")
            failed += 1
            if url:
                time.sleep(0.8)
            continue

        try:
            _upsert_specs(cfg, pid, specs)
            _mark_status(pid, "ok")
            log.info(f"  ok pid={pid} [{slug}] {title[:50]}")
            ok += 1
        except Exception as exc:
            log.error(f"  pid={pid} DB write failed: {exc}")
            _mark_status(pid, "failed")
            failed += 1

        time.sleep(0.8)

    return {"ok": ok, "skipped": skipped, "failed": failed}
