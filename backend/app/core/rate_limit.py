"""Simple in-memory rate limiter — no external dependencies required."""

import time
from collections import defaultdict

from fastapi import HTTPException, Request

# { "prefix:ip": [timestamp, ...] }
_windows: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(
    request: Request,
    max_calls: int = 10,
    window: int = 60,
    key_prefix: str = "global",
) -> None:
    """
    Raises HTTP 429 if the caller exceeds max_calls within `window` seconds.
    Key is composed of key_prefix + client IP (respects X-Forwarded-For).
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    key = f"{key_prefix}:{client_ip}"
    now = time.monotonic()

    # Slide the window — discard expired timestamps
    valid = [t for t in _windows[key] if now - t < window]

    if len(valid) >= max_calls:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please wait {window} seconds and try again.",
        )

    valid.append(now)
    _windows[key] = valid
