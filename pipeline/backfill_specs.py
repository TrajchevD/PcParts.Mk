"""
backfill_specs.py — Fill NULL optional fields in cpu_specs and gpu_specs
using the reference lookup tables in enrichment/specs_db.py.

Usage:
    python backfill_specs.py             # dry-run (shows what would change)
    python backfill_specs.py --apply     # write changes to DB
    python backfill_specs.py --table cpu # only backfill CPU specs
    python backfill_specs.py --table gpu # only backfill GPU specs
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding="utf-8")

from db import fetchall, execute
from enrichment.specs_db import lookup_cpu, lookup_gpu

log = logging.getLogger("backfill_specs")

# Fields we'll attempt to fill per table
CPU_OPTIONAL = ["cores", "threads", "base_clock_ghz", "boost_clock_ghz", "tdp_w", "memory_type"]
GPU_OPTIONAL = ["memory_type", "pcie_version", "recommended_psu_w", "vram_gb"]


def _backfill_cpu(apply: bool) -> dict:
    rows = fetchall("""
        SELECT cs.product_id, cs.cpu_model,
               cs.cores, cs.threads, cs.base_clock_ghz,
               cs.boost_clock_ghz, cs.tdp_w, cs.memory_type
        FROM cpu_specs cs
        WHERE cs.cores IS NULL
           OR cs.threads IS NULL
           OR cs.base_clock_ghz IS NULL
           OR cs.boost_clock_ghz IS NULL
           OR cs.tdp_w IS NULL
           OR cs.memory_type IS NULL
    """)

    if not rows:
        log.info("[CPU] No rows with NULL optional fields.")
        return {"checked": 0, "matched": 0, "updated": 0, "fields_filled": 0}

    log.info(f"[CPU] {len(rows)} rows have at least one NULL optional field")

    matched = updated = fields_filled = 0

    for row in rows:
        model = row["cpu_model"] or ""
        ref = lookup_cpu(model)
        if not ref:
            continue
        matched += 1

        updates = {}
        for field in CPU_OPTIONAL:
            if row[field] is None and ref.get(field) is not None:
                updates[field] = ref[field]

        if not updates:
            continue

        field_log = ", ".join(f"{k}={v}" for k, v in updates.items())
        log.info(f"  pid={row['product_id']} model={model!r} → {field_log}")

        if apply:
            set_clause = ", ".join(f"{k}=%s" for k in updates)
            vals = list(updates.values()) + [row["product_id"]]
            execute(
                f"UPDATE cpu_specs SET {set_clause} WHERE product_id=%s",
                tuple(vals),
            )
            updated += 1
            fields_filled += len(updates)

    if not apply:
        log.info(f"[CPU] DRY-RUN — would update {matched} rows (use --apply to write)")
    else:
        log.info(f"[CPU] Updated {updated}/{matched} matched rows, {fields_filled} fields filled")

    return {
        "checked": len(rows),
        "matched": matched,
        "updated": updated if apply else 0,
        "fields_filled": fields_filled if apply else 0,
    }


def _backfill_gpu(apply: bool) -> dict:
    rows = fetchall("""
        SELECT gs.product_id, gs.gpu_model,
               gs.memory_type, gs.pcie_version, gs.recommended_psu_w, gs.vram_gb
        FROM gpu_specs gs
        WHERE gs.memory_type IS NULL
           OR gs.pcie_version IS NULL
           OR gs.recommended_psu_w IS NULL
           OR gs.vram_gb IS NULL
    """)

    if not rows:
        log.info("[GPU] No rows with NULL optional fields.")
        return {"checked": 0, "matched": 0, "updated": 0, "fields_filled": 0}

    log.info(f"[GPU] {len(rows)} rows have at least one NULL optional field")

    matched = updated = fields_filled = 0

    for row in rows:
        model = row["gpu_model"] or ""
        ref = lookup_gpu(model)
        if not ref:
            continue
        matched += 1

        updates = {}
        for field in GPU_OPTIONAL:
            if row[field] is None and ref.get(field) is not None:
                updates[field] = ref[field]

        if not updates:
            continue

        field_log = ", ".join(f"{k}={v}" for k, v in updates.items())
        log.info(f"  pid={row['product_id']} model={model!r} → {field_log}")

        if apply:
            set_clause = ", ".join(f"{k}=%s" for k in updates)
            vals = list(updates.values()) + [row["product_id"]]
            execute(
                f"UPDATE gpu_specs SET {set_clause} WHERE product_id=%s",
                tuple(vals),
            )
            updated += 1
            fields_filled += len(updates)

    if not apply:
        log.info(f"[GPU] DRY-RUN — would update {matched} rows (use --apply to write)")
    else:
        log.info(f"[GPU] Updated {updated}/{matched} matched rows, {fields_filled} fields filled")

    return {
        "checked": len(rows),
        "matched": matched,
        "updated": updated if apply else 0,
        "fields_filled": fields_filled if apply else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Backfill NULL spec fields from reference DB")
    parser.add_argument(
        "--apply", action="store_true",
        help="Write changes to DB (default: dry-run, just shows what would change)",
    )
    parser.add_argument(
        "--table", choices=["cpu", "gpu", "all"], default="all",
        help="Which spec table to backfill (default: all)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    mode = "APPLY" if args.apply else "DRY-RUN"
    log.info("=" * 55)
    log.info(f"  Spec Backfill  [{mode}]  table={args.table}")
    log.info("=" * 55)

    cpu_stats = gpu_stats = {}

    if args.table in ("cpu", "all"):
        cpu_stats = _backfill_cpu(apply=args.apply)

    if args.table in ("gpu", "all"):
        gpu_stats = _backfill_gpu(apply=args.apply)

    log.info("=" * 55)
    log.info("  Summary")
    log.info("=" * 55)
    if cpu_stats:
        log.info(
            f"  CPU  checked={cpu_stats['checked']}  matched={cpu_stats['matched']}  "
            f"updated={cpu_stats['updated']}  fields={cpu_stats['fields_filled']}"
        )
    if gpu_stats:
        log.info(
            f"  GPU  checked={gpu_stats['checked']}  matched={gpu_stats['matched']}  "
            f"updated={gpu_stats['updated']}  fields={gpu_stats['fields_filled']}"
        )
    if not args.apply:
        log.info("  (dry-run — re-run with --apply to write changes)")
    log.info("=" * 55)


if __name__ == "__main__":
    main()
