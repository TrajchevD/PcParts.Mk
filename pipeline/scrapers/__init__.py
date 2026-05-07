import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from scrapers.anhoch  import run as run_anhoch
from scrapers.neptune import run as run_neptune
from scrapers.setec   import run as run_setec
from scrapers.gjirafa import run as run_gjirafa

log = logging.getLogger("pipeline.scrapers")

# requests-based — thread-safe, run in parallel
_PARALLEL = [
    ("Anhoch",    run_anhoch),
    ("Gjirafa50", run_gjirafa),
]

# Playwright-based — each creates its own browser; run sequentially to save memory
_SEQUENTIAL = [
    ("Neptun", run_neptune),
    ("Setec",  run_setec),
]


def run_all() -> dict[str, list]:
    results: dict[str, list] = {}

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(fn): name for name, fn in _PARALLEL}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
                log.info(f"[{name}] {len(results[name])} products")
            except Exception as exc:
                log.error(f"[{name}] scraper failed: {exc}")
                results[name] = []

    for name, fn in _SEQUENTIAL:
        try:
            results[name] = fn()
            log.info(f"[{name}] {len(results[name])} products")
        except Exception as exc:
            log.error(f"[{name}] scraper failed: {exc}")
            results[name] = []

    total = sum(len(v) for v in results.values())
    log.info(f"All scrapers done — {total} products total")
    return results
