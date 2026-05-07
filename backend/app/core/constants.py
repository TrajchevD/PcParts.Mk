"""Application-wide constants — single source of truth for all magic numbers."""

# ─── Database ────────────────────────────────────────────────────
DB_POOL_SIZE = 10

# ─── Pagination ──────────────────────────────────────────────────
DEFAULT_PAGE_LIMIT = 24
MAX_PAGE_LIMIT = 200
BUILDER_PAGE_LIMIT = 20
COMPARE_MAX_ITEMS = 4

# ─── Outlier / Pricing filter ────────────────────────────────────
# Offers priced below (model_avg * OUTLIER_PRICE_RATIO) are excluded
# as likely mislabelled bundles or data errors.
OUTLIER_PRICE_RATIO = 0.70

# ─── Recommendations ─────────────────────────────────────────────
STANDARD_PSU_SIZES = [450, 550, 650, 750, 850, 1000]
PSU_OVERHEAD_FACTOR = 1.30      # 30 % headroom above estimated TDP+platform
PSU_CPU_BASE_OVERHEAD_W = 120   # Watts added for platform (VRMs, storage, etc.)
PSU_DEFAULT_TDP_W = 65          # Assumed CPU TDP when unknown
PSU_DEFAULT_GPU_REC_W = 500     # Assumed GPU requirement when unknown

# ─── VRAM tier thresholds (from CPU core count) ──────────────────
VRAM_HIGH_CORES_THRESHOLD = 12
VRAM_MID_CORES_THRESHOLD = 8
VRAM_HIGH_GB = 12
VRAM_MID_GB = 8
VRAM_LOW_GB = 6

# ─── Alerts ──────────────────────────────────────────────────────
ALERT_MATCH_LIMIT = 8           # Max matching offers per alert notification
ALERT_SCHEDULE_MINUTES = 30     # How often the background checker runs

# ─── Rate limits ─────────────────────────────────────────────────
AUTH_RATE_LIMIT = 10            # Requests per window
AUTH_RATE_WINDOW = 60           # Window in seconds (1 minute)

# ─── Cache TTLs (seconds) ────────────────────────────────────────
CACHE_TTL_PRODUCTS = 300        # 5 minutes
CACHE_TTL_SPECS = 3600          # 1 hour
CACHE_TTL_RECOMMENDATIONS = 600 # 10 minutes
