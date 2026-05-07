import os

from dotenv import load_dotenv

load_dotenv()

# ─── Database ─────────────────────────────────────────────────────
DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
DB_USER: str = os.getenv("DB_USER", "root")
DB_PASS: str = os.getenv("DB_PASS", "")
DB_NAME: str = os.getenv("DB_NAME", "pc_parts")

# ─── JWT ──────────────────────────────────────────────────────────
JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# ─── Admin API Key ────────────────────────────────────────────────
# Used to protect privileged endpoints (e.g. /api/alerts/check).
# Generate with: python -c "import secrets; print(secrets.token_hex(16))"
ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")

# ─── CORS ─────────────────────────────────────────────────────────
CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

# ─── Runtime environment ──────────────────────────────────────────
ENV: str = os.getenv("ENV", "development")


_INSECURE_JWT_DEFAULT = "change-me-in-production"


def validate_config() -> list[str]:
    """
    Returns a list of human-readable security warnings.
    Called once at application startup.
    """
    warnings: list[str] = []

    if JWT_SECRET == _INSECURE_JWT_DEFAULT:
        warnings.append(
            "JWT_SECRET is the insecure default value. "
            'Generate a strong secret: python -c "import secrets; print(secrets.token_hex(32))"'
        )

    if not ADMIN_API_KEY:
        warnings.append(
            "ADMIN_API_KEY is not set — the /api/alerts/check endpoint will return 503. "
            'Generate one: python -c "import secrets; print(secrets.token_hex(16))"'
        )

    return warnings
