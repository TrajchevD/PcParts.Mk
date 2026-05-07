"""
Parallel enrichment engine.

Architecture:
  - ThreadPoolExecutor for concurrent HTTP + parsing
  - Per-domain semaphores prevent hammering any single site
  - Multi-round retry loop with exponential backoff between rounds
  - Thread-safe DB writes via the existing connection pool
  - All HTML responses cached on disk (enrichment/cache.py)
  - Metrics tracked throughout and logged at completion

Job lifecycle:
  pending → [parse attempt] → ok | retry
  retry × MAX_RETRIES → failed
"""
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from db import fetchall, execute
from enrichment.choose_offer import pick_best_offer
from enrichment.metrics import Metrics
from enrichment.parsers.cpu     import parse as parse_cpu
from enrichment.parsers.gpu     import parse as parse_gpu
from enrichment.parsers.mb      import parse as parse_mb
from enrichment.parsers.ram     import parse as parse_ram
from enrichment.parsers.storage import parse as parse_storage

log = logging.getLogger("pipeline.enrichment.parallel")

# ── Per-domain concurrency limits ────────────────────────────────────────────
# Playwright stores get lower limits to avoid OOM / page timeouts
_DOMAIN_SEMS: dict[str, threading.Semaphore] = {
    "anhoch.com": threading.Semaphore(8),
    "gjirafa50":  threading.Semaphore(5),
    "neptun.mk":  threading.Semaphore(2),
    "setec.mk":   threading.Semaphore(2),
}
_DEFAULT_SEM = threading.Semaphore(6)

MAX_RETRIES = 4
RETRY_BASE  = 2.0  # delay for round N = RETRY_BASE ** N  (2s, 4s, 8s, 16s)

# ── Parser / spec-table registry ─────────────────────────────────────────────
PARSERS = {
    "cpu":     parse_cpu,
    "gpu":     parse_gpu,
    "mb":      parse_mb,
    "ram":     parse_ram,
    "storage": parse_storage,
    "memory":  parse_storage,
}

SPEC_TABLES: dict[str, dict] = {
    "cpu": {
        "table": "cpu_specs",
        "cols":  ["product_id", "cpu_model", "brand", "socket", "cores",
                  "threads", "base_clock_ghz", "boost_clock_ghz", "tdp_w", "memory_type"],
        "keys":  ["cpu_model", "brand", "socket", "cores", "threads",
                  "base_clock_ghz", "boost_clock_ghz", "tdp_w", "memory_type"],
        "required": ["socket"],
    },
    "gpu": {
        "table": "gpu_specs",
        "cols":  ["product_id", "gpu_model", "vram_gb", "memory_type",
                  "pcie_version", "length_mm", "recommended_psu_w"],
        "keys":  ["gpu_model", "vram_gb", "memory_type", "pcie_version",
                  "length_mm", "recommended_psu_w"],
        "required": ["gpu_model", "vram_gb"],
    },
    "mb": {
        "table": "mb_specs",
        "cols":  ["product_id", "mb_model", "brand", "chipset", "socket",
                  "form_factor", "memory_type", "memory_slots", "max_memory_gb", "pcie_version"],
        "keys":  ["mb_model", "brand", "chipset", "socket", "form_factor",
                  "memory_type", "memory_slots", "max_memory_gb", "pcie_version"],
        "required": ["socket", "memory_type"],
    },
    "ram": {
        "table": "ram_specs",
        "cols":  ["product_id", "brand", "series", "memory_type", "total_capacity_gb",
                  "sticks", "capacity_per_stick_gb", "speed_mhz", "cas_latency",
                  "expo", "xmp", "ecc"],
        "keys":  ["brand", "series", "memory_type", "total_capacity_gb",
                  "sticks", "capacity_per_stick_gb", "speed_mhz", "cas_latency",
                  "expo", "xmp", "ecc"],
        "required": ["memory_type", "total_capacity_gb"],
    },
    "storage": {
        "table": "storage_specs",
        "cols":  ["product_id", "type", "brand", "series", "capacity_gb",
                  "form_factor", "interface", "pcie_version", "rpm"],
        "keys":  ["type", "brand", "series", "capacity_gb",
                  "form_factor", "interface", "pcie_version", "rpm"],
        "required": ["type", "capacity_gb"],
    },
}
SPEC_TABLES["memory"] = SPEC_TABLES["storage"]


# ── Internal helpers ─────────────────────────────────────────────────────────

def _domain_sem(url: str) -> threading.Semaphore:
    domain = urlparse(url or "").netloc.lower()
    for key, sem in _DOMAIN_SEMS.items():
        if key in domain:
            return sem
    return _DEFAULT_SEM


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
    execute(
        "UPDATE products SET spec_status=%s WHERE product_id=%s",
        (status, product_id),
    )


# ── Per-product worker ────────────────────────────────────────────────────────

def _process_one(p: dict, metrics: Metrics) -> str:
    """
    Attempt to enrich one product.
    Returns: 'ok' | 'skipped' | 'retry' | 'failed'
    """
    pid    = p["product_id"]
    slug   = p["category"]
    cfg    = SPEC_TABLES.get(slug)
    parser = PARSERS.get(slug)

    if not cfg or not parser:
        metrics.inc(skipped=1)
        return "skipped"

    offer = pick_best_offer(pid)
    if not offer:
        metrics.inc(skipped=1)
        return "skipped"

    title = offer["title_raw"] or p.get("canonical_title", "")
    url   = offer["product_url"] or ""

    sem = _domain_sem(url)
    with sem:
        try:
            specs = parser(title, url)
        except Exception as exc:
            err = str(exc).lower()
            if any(k in err for k in ("connection", "timeout", "reset", "refused", "remote end")):
                metrics.inc(network_errors=1)
                log.debug(f"pid={pid} [{slug}] network error: {exc}")
            else:
                metrics.inc(parse_errors=1)
                log.warning(f"pid={pid} [{slug}] parser exception: {exc}")
            return "retry"

    if not specs or not all(specs.get(k) is not None for k in cfg["required"]):
        missing = [k for k in cfg["required"] if not specs or specs.get(k) is None]
        log.debug(f"pid={pid} [{slug}] missing={missing}: {title[:60]}")
        metrics.inc(structural_errors=1)
        return "retry"

    try:
        _upsert_specs(cfg, pid, specs)
        _mark_status(pid, "ok")
        log.info(f"ok  pid={pid:>6} [{slug:<8}] {title[:55]}")
        metrics.inc(ok=1)
        return "ok"
    except Exception as exc:
        log.error(f"pid={pid} DB write error: {exc}")
        metrics.inc(parse_errors=1)
        return "retry"


# ── Public entry point ───────────────────────────────────────────────────────

def run_parallel(
    limit: int = 0,
    include_failed: bool = False,
    workers: int = 8,
) -> dict:
    """
    Run enrichment in parallel with multi-round exponential-backoff retries.

    limit:          max products to process (0 = unlimited — processes everything)
    include_failed: also re-attempt products previously marked 'failed'
    workers:        max concurrent threads
    """
    status_filter = "'pending', 'failed'" if include_failed else "'pending'"
    limit_clause  = f"LIMIT {limit}" if limit > 0 else ""

    products = fetchall(
        f"""
        SELECT p.product_id, c.slug AS category, p.canonical_title
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE p.spec_status IN ({status_filter})
        ORDER BY p.product_id DESC
        {limit_clause}
        """,
    )

    if not products:
        log.info("No products to enrich — nothing to do")
        return {
            "total": 0, "ok": 0, "skipped": 0, "failed": 0,
            "retried": 0, "elapsed_min": 0.0, "success_rate_pct": 0.0,
            "throughput_per_min": 0.0,
        }

    log.info(
        f"Parallel enrichment start | products={len(products)} "
        f"workers={workers} include_failed={include_failed}"
    )
    metrics  = Metrics()
    t_start  = time.time()
    t_ok     = 0
    t_skip   = 0
    t_fail   = 0
    t_retry  = 0
    pending  = list(products)

    for attempt in range(MAX_RETRIES + 1):
        if not pending:
            break

        if attempt > 0:
            delay = RETRY_BASE ** attempt
            log.info(
                f"Retry round {attempt}/{MAX_RETRIES} | "
                f"products={len(pending)} backoff={delay:.1f}s"
            )
            t_retry += len(pending)
            metrics.inc(retried=len(pending))
            time.sleep(delay)

        retry_list: list[dict] = []

        with ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="enrich",
        ) as pool:
            future_map = {
                pool.submit(_process_one, p, metrics): p
                for p in pending
            }
            done = 0
            total_batch = len(pending)
            for future in as_completed(future_map):
                p = future_map[future]
                try:
                    result = future.result()
                except Exception as exc:
                    log.error(f"pid={p['product_id']} unhandled worker exception: {exc}")
                    result = "retry"

                if result == "ok":
                    t_ok += 1
                elif result == "skipped":
                    t_skip += 1
                elif result == "retry":
                    retry_list.append(p)
                else:  # explicit "failed"
                    _mark_status(p["product_id"], "failed")
                    t_fail += 1

                done += 1
                if done % 50 == 0 or done == total_batch:
                    elapsed = time.time() - t_start
                    rate    = (t_ok + t_skip + t_fail) / elapsed * 60 if elapsed > 0 else 0
                    log.info(
                        f"  Progress {done}/{total_batch} | "
                        f"ok={t_ok} skip={t_skip} fail={t_fail} retry_q={len(retry_list)} "
                        f"rate={rate:.1f}/min"
                    )

        pending = retry_list

    # Exhaust: products that failed all MAX_RETRIES rounds
    for p in pending:
        _mark_status(p["product_id"], "failed")
        t_fail += 1

    total    = t_ok + t_skip + t_fail
    elapsed  = (time.time() - t_start) / 60
    success  = (t_ok / total * 100) if total > 0 else 0.0
    throughput = (total / elapsed) if elapsed > 0 else 0.0

    summary = {
        "total":              total,
        "ok":                 t_ok,
        "skipped":            t_skip,
        "failed":             t_fail,
        "retried":            t_retry,
        "elapsed_min":        round(elapsed, 1),
        "success_rate_pct":   round(success, 1),
        "throughput_per_min": round(throughput, 1),
    }
    log.info(
        f"Enrichment done | ok={t_ok} skip={t_skip} fail={t_fail} "
        f"retry_attempts={t_retry} success={success:.1f}% "
        f"throughput={throughput:.1f}/min elapsed={elapsed:.1f}min"
    )
    return summary
