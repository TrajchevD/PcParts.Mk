"""
scheduler.py — persistent server that runs the pipeline on a schedule.

Start:  python scheduler.py
Stop:   Ctrl+C

On startup the pipeline runs immediately, then repeats every
SCRAPE_INTERVAL_HOURS (set in .env, default 6).
"""
import logging
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import SCRAPE_INTERVAL_HOURS
from pipeline import run_pipeline, _setup_logging


def main():
    _setup_logging()
    log = logging.getLogger("scheduler")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(hours=SCRAPE_INTERVAL_HOURS),
        id="pipeline",
        name="PcPartsMK full pipeline",
        misfire_grace_time=300,
        coalesce=True,
        next_run_time=datetime.now(),   # run immediately on startup
    )

    log.info(f"Scheduler started — pipeline runs every {SCRAPE_INTERVAL_HOURS}h")
    log.info("Press Ctrl+C to stop")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped")


if __name__ == "__main__":
    main()
