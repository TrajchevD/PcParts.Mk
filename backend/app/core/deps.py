from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import ADMIN_API_KEY
from app.core.security import decode_token

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """Validates the Bearer JWT and returns the decoded payload."""
    try:
        return decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_admin_key(x_api_key: str = Header(default="")) -> None:
    """
    Validates the X-API-Key header against ADMIN_API_KEY.
    Apply as a dependency on admin-only endpoints.
    """
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "Admin API key not configured on this server. "
                "Set ADMIN_API_KEY in your .env file."
            ),
        )
    if not x_api_key or x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing admin API key")
