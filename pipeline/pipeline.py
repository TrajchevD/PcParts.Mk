"""
pipeline.py — run manually or imported by scheduler.py

Usage:
    python pipeline.py                   # full run (scrape + parallel enrich)
    python pipeline.py --phase scrape    # scrape + load only
    python pipeline.py --phase enrich    # enrichment only
    python pipeline.py --dry-run         # scrape but skip DB writes
    python pipeline.py --workers 12      # override enrichment concurrency
"""
import argparse
import logging
import sys
import time

from enrichment import run_enrichment_parallel
from scrapers import run_all as scrape_all
from loader import upsert_offer, mark_all_out_of_stock

log = logging.getLogger("pipeline")

# Default enrichment worker count — can be overridden via CLI or env
import os
DEFAULT_WORKERS = int(os.getenv("ENRICH_WORKERS", "8"))


def _load_store(store_name: str, products: list) -> dict:
    if not products:
        return {"scraped": 0, "loaded": 0}
    mark_all_out_of_stock(store_name)
    loaded = 0
    for p in products:
        p["store"] = store_name
        try:
            upsert_offer(p)
            loaded += 1
        except Exception as exc:
            log.warning(f"[{store_name}] upsert failed: {exc}")
    log.info(f"[{store_name}] {loaded}/{len(products)} loaded")
    return {"scraped": len(products), "loaded": loaded}


def run_scrape_and_load(dry_run: bool = False) -> dict:
    store_data = scrape_all()
    summary = {}
    for store_name, products in store_data.items():
        if dry_run:
            log.info(f"[{store_name}] DRY-RUN — {len(products)} scraped, skipping DB")
            summary[store_name] = {"scraped": len(products), "loaded": 0, "dry_run": True}
        else:
            summary[store_name] = _load_store(store_name, products)
    return summary


def run_pipeline(
    dry_run: bool = False,
    phase: str = "all",
    retry_failed: bool = False,
    workers: int = DEFAULT_WORKERS,
) -> dict:
    log.info("=" * 55)
    log.info(
        f"Pipeline starting  phase={phase}  dry_run={dry_run}  "
        f"retry_failed={retry_failed}  workers={workers}"
    )
    t0 = time.time()

    scrape_summary = {}
    enrich_stats   = {}

    if phase in ("scrape", "all"):
        scrape_summary = run_scrape_and_load(dry_run=dry_run)

    if phase in ("enrich", "all") and not dry_run:
        enrich_stats = run_enrichment_parallel(
            limit=0,                     # process all pending (no artificial cap)
            include_failed=retry_failed,
            workers=workers,
        )

    elapsed = time.time() - t0
    log.info(f"Pipeline done in {elapsed / 60:.1f} min")
    if enrich_stats:
        log.info(
            f"Enrich: ok={enrich_stats.get('ok')} "
            f"skipped={enrich_stats.get('skipped')} "
            f"failed={enrich_stats.get('failed')} "
            f"success={enrich_stats.get('success_rate_pct')}%"
        )
    log.info("=" * 55)
    return {"scrape": scrape_summary, "enrich": enrich_stats}


def _setup_logging():
    import io
    stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%H:%M:%S"
    ))
    logging.basicConfig(level=logging.INFO, handlers=[handler])


if __name__ == "__main__":
    _setup_logging()
    parser = argparse.ArgumentParser(description="PcPartsMK pipeline")
    parser.add_argument("--phase", choices=["scrape", "enrich", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Re-attempt enrichment for previously-failed products")
    parser.add_argument("--store", help="Scrape a single store only (e.g. Neptun)")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                        help=f"Enrichment worker threads (default: {DEFAULT_WORKERS})")
    args = parser.parse_args()

    if args.store:
        from scrapers import _PARALLEL, _SEQUENTIAL
        store_map = {name: fn for name, fn in _PARALLEL + _SEQUENTIAL}
        name = args.store
        fn = store_map.get(name)
        if not fn:
            log.error(f"Unknown store '{name}'. Available: {list(store_map)}")
            os._exit(1)
        log.info(f"Running single-store scrape: {name}")
        products = fn()
        _load_store(name, products)
    else:
        run_pipeline(
            dry_run=args.dry_run,
            phase=args.phase,
            retry_failed=args.retry_failed,
            workers=args.workers,
        )

    # Force-exit to kill any lingering Playwright/Chromium subprocesses immediately
    os._exit(0)
