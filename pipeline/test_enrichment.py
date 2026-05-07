"""
Dry-run enrichment tester — fetches real offer URLs from the DB,
runs parsers, prints results. No data is written to the database.

Usage:
    python test_enrichment.py              # all categories
    python test_enrichment.py cpu gpu mb   # specific categories
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from db import fetchall
from enrichment.parsers.cpu     import parse as parse_cpu
from enrichment.parsers.gpu     import parse as parse_gpu
from enrichment.parsers.mb      import parse as parse_mb
from enrichment.parsers.ram     import parse as parse_ram
from enrichment.parsers.storage import parse as parse_storage

PARSERS = {
    "cpu":     parse_cpu,
    "gpu":     parse_gpu,
    "mb":      parse_mb,
    "ram":     parse_ram,
    "storage": parse_storage,
}

REQUIRED = {
    "cpu":     ["socket"],
    "gpu":     ["vram_gb"],
    "mb":      ["socket", "memory_type"],
    "ram":     ["memory_type", "total_capacity_gb"],
    "storage": ["type", "capacity_gb"],
}

SAMPLES = 3


def test_category(slug: str, parser) -> None:
    rows = fetchall(
        """
        SELECT po.title_raw, po.product_url, p.canonical_title, s.name AS store
        FROM product_offers po
        JOIN products p ON p.product_id = po.product_id
        JOIN categories c ON c.category_id = p.category_id
        JOIN stores s ON s.store_id = po.store_id
        WHERE c.slug = %s
          AND po.product_url IS NOT NULL
          AND po.product_url <> ''
        ORDER BY
            (s.name = 'Anhoch') DESC,
            po.offer_id DESC
        LIMIT %s
        """,
        (slug, SAMPLES),
    )
    if not rows:
        print("  [no rows found in DB for this category]")
        return

    required  = REQUIRED.get(slug, [])
    passed    = 0
    rejected  = 0   # parser returned None
    by_store  = {}  # store -> [ok, total]

    for row in rows:
        title = row["title_raw"] or row["canonical_title"]
        url   = row["product_url"]
        store = row["store"]
        by_store.setdefault(store, [0, 0])
        by_store[store][1] += 1

        try:
            specs = parser(title, url)
        except Exception as exc:
            print(f"  EXCEPTION [{store}] {title[:60]}")
            print(f"    {exc}")
            continue

        if specs is None:
            rejected += 1
            print(f"  NONE     [{store}] {title[:70]}")
            continue

        missing = [k for k in required if specs.get(k) is None]
        if missing:
            status = "MISSING"
        else:
            passed += 1
            by_store[store][0] += 1
            status = "OK"

        print(f"\n  [{status}] [{store}] {title[:65]}")
        for k, v in specs.items():
            if v is not None:
                print(f"    {k:<24} {v}")
        if missing:
            print(f"    *** missing: {missing}")

    total = len(rows)
    print(f"\n  {'-'*56}")
    print(f"  TOTAL   : {passed}/{total} passed  |  {rejected} returned None")
    print(f"  By store:")
    for store, (ok, tot) in sorted(by_store.items()):
        print(f"    {store:<12} {ok}/{tot}")
    print()


def main() -> None:
    cats = sys.argv[1:] or list(PARSERS.keys())
    for slug in cats:
        if slug not in PARSERS:
            print(f"Unknown category '{slug}'. Valid: {list(PARSERS)}")
            continue
        print(f"\n{'=' * 60}")
        print(f"  {slug.upper()}")
        print(f"{'=' * 60}")
        test_category(slug, PARSERS[slug])


if __name__ == "__main__":
    main()
