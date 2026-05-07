import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS, validate_config
from app.core.constants import ALERT_SCHEDULE_MINUTES
from app.routers import auth, alerts, notifications, builder, compare, recommend, users
from app.routers.products import cpu, gpu, mb, ram, storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Background scheduler ─────────────────────────────────────────

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    _SCHEDULER_AVAILABLE = True
except ImportError:
    _SCHEDULER_AVAILABLE = False
    logger.warning(
        "apscheduler not installed — background alert checker disabled. "
        "Run: pip install apscheduler"
    )

_scheduler = None


def _run_alert_checks_safe() -> None:
    """Wrapper that prevents the scheduler from crashing if the checker fails."""
    try:
        from app.services.alert_checker import run_alert_checks
        result = run_alert_checks()
        if result.get("triggered"):
            logger.info("Alert scheduler: triggered %d alert(s).", result["triggered"])
    except Exception as exc:
        logger.exception("Alert scheduler error: %s", exc)


# ─── App lifespan ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    warnings = validate_config()
    for w in warnings:
        logger.warning("CONFIG WARNING: %s", w)

    global _scheduler
    if _SCHEDULER_AVAILABLE:
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.add_job(
            _run_alert_checks_safe,
            "interval",
            minutes=ALERT_SCHEDULE_MINUTES,
            id="alert_checker",
            replace_existing=True,
        )
        _scheduler.start()
        logger.info(
            "Background alert checker started (interval: %d min).",
            ALERT_SCHEDULE_MINUTES,
        )

    yield

    # Shutdown
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler shut down.")


# ─── Application ──────────────────────────────────────────────────

app = FastAPI(
    title="PcPartsMk API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────
# Restrict to explicit origins, methods, and headers only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


# ─── Security headers middleware ──────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    # Remove server version disclosure (MutableHeaders uses del, not pop)
    try:
        del response.headers["server"]
    except KeyError:
        pass
    return response


# ─── Request logging middleware ───────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start = time.monotonic()
    response = await call_next(request)
    elapsed_ms = round((time.monotonic() - start) * 1000, 1)
    logger.debug(
        "%s %s → %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ─── Routers ──────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(notifications.router)
app.include_router(builder.router)
app.include_router(compare.router)
app.include_router(recommend.router)

# Product listings
app.include_router(cpu.router)
app.include_router(gpu.router)
app.include_router(mb.router)
app.include_router(ram.router)
app.include_router(storage.router)


# ─── Health ───────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "version": "2.0.0"}
