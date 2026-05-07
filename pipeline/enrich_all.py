"""
Autonomous enrichment loop.

Runs the parallel enrichment engine in repeated rounds until spec coverage
stabilizes (improvement drops below --min-improvement) or --max-rounds is hit.

Usage:
    python enrich_all.py                         # single pass, all pending
    python enrich_all.py --include-failed        # include previously failed
    python enrich_all.py --workers 12            # set concurrency
    python enrich_all.py --loop                  # run until stable
    python enrich_all.py --loop --max-rounds 10  # cap at 10 rounds
    python enrich_all.py --loop --min-improvement 5  # stop if <5 new OK per round
"""
import argparse
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding="utf-8")

from db import fetchall
from enrichment.parallel_runner import run_parallel


# ── Coverage helpers ──────────────────────────────────────────────────────────

def _coverage() -> dict[str, dict[str, int]]:
    rows = fetchall("""
        SELECT c.slug, p.spec_status, COUNT(*) AS cnt
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        GROUP BY c.slug, p.spec_status
        ORDER BY c.slug, p.spec_status
    """)
    report: dict[str, dict[str, int]] = {}
    for r in rows:
        slug   = r["slug"]
        status = r["spec_status"]
        cnt    = int(r["cnt"])
        if slug not in report:
            report[slug] = {"ok": 0, "pending": 0, "failed": 0}
        report[slug][status] = cnt
    return report


def _print_coverage(report: dict, log: logging.Logger) -> None:
    log.info("─" * 60)
    log.info(f"  {'Category':<12}{'OK':>7}{'Pending':>9}{'Failed':>8}{'Coverage':>10}")
    log.info("─" * 60)
    total_ok = total_all = 0
    for slug in sorted(report):
        d    = report[slug]
        ok   = d.get("ok", 0)
        pend = d.get("pending", 0)
        fail = d.get("failed", 0)
        tot  = ok + pend + fail
        pct  = ok / tot * 100 if tot > 0 else 0.0
        log.info(f"  {slug:<12}{ok:>7}{pend:>9}{fail:>8}{pct:>9.1f}%")
        total_ok  += ok
        total_all += tot
    log.info("─" * 60)
    overall = total_ok / total_all * 100 if total_all > 0 else 0.0
    log.info(
        f"  {'TOTAL':<12}{total_ok:>7}{'':>9}{'':>8}{overall:>9.1f}%  "
        f"({total_all} products)"
    )
    log.info("─" * 60)


def _count_ok(report: dict) -> int:
    return sum(d.get("ok", 0) for d in report.values())


def _count_pending(report: dict) -> int:
    return sum(d.get("pending", 0) for d in report.values())


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Autonomous parallel enrichment loop for PcPartsMK"
    )
    parser.add_argument(
        "--include-failed", action="store_true",
        help="Also retry products previously marked 'failed'",
    )
    parser.add_argument(
        "--workers", type=int, default=int(os.getenv("ENRICH_WORKERS", "8")),
        help="Concurrent worker threads (default: 8 or $ENRICH_WORKERS)",
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="Run multiple rounds until coverage stabilizes",
    )
    parser.add_argument(
        "--max-rounds", type=int, default=5,
        help="Max rounds when --loop is active (default: 5)",
    )
    parser.add_argument(
        "--min-improvement", type=int, default=1,
        help="Stop looping if fewer than N new products enriched per round (default: 1)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log = logging.getLogger("enrich_all")

    max_rounds = args.max_rounds if args.loop else 1
    log.info("=" * 60)
    log.info("  PcPartsMK — Autonomous Enrichment Pipeline")
    log.info(f"  workers={args.workers}  loop={args.loop}  max_rounds={max_rounds}")
    log.info(f"  include_failed={args.include_failed}")
    log.info("=" * 60)

    t_global = time.time()
    prev_ok  = None

    for round_num in range(1, max_rounds + 1):
        log.info(f"\n{'='*60}")
        log.info(f"  Round {round_num}/{max_rounds}")
        log.info(f"{'='*60}")

        report_before = _coverage()
        log.info("Coverage BEFORE:")
        _print_coverage(report_before, log)
        ok_before = _count_ok(report_before)

        # After the first round, always include_failed to give them another chance
        include_failed = args.include_failed or (round_num > 1)

        summary = run_parallel(
            limit=0,
            include_failed=include_failed,
            workers=args.workers,
        )

        log.info(f"\nRound {round_num} results:")
        for k, v in summary.items():
            log.info(f"  {k:<22} {v}")

        report_after = _coverage()
        ok_after     = _count_ok(report_after)
        improvement  = ok_after - ok_before
        pending_left = _count_pending(report_after)

        log.info(f"\nCoverage AFTER (round {round_num}):")
        _print_coverage(report_after, log)
        log.info(f"  Improvement this round: +{improvement} products enriched")
        log.info(f"  Pending remaining:       {pending_left}")

        if args.loop:
            if pending_left == 0:
                log.info("All products processed — stopping loop early")
                break
            if prev_ok is not None and improvement < args.min_improvement:
                log.info(
                    f"Improvement ({improvement}) < threshold ({args.min_improvement}) "
                    f"— coverage has stabilized"
                )
                break

        prev_ok = ok_after

    elapsed_total = (time.time() - t_global) / 60
    log.info(f"\n{'='*60}")
    log.info("  FINAL COVERAGE")
    log.info(f"{'='*60}")
    _print_coverage(_coverage(), log)
    log.info(f"  Total elapsed: {elapsed_total:.1f} min")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
