"""
Disk-backed HTML response cache with TTL.
Thread-safe writes; reads are lock-free (file-system atomicity is sufficient).
Cache files are gzip-compressed and stored under .html_cache/ next to the pipeline root.
"""
import gzip
import hashlib
import os
import time
from pathlib import Path
from threading import Lock

_CACHE_DIR = Path(os.getenv(
    "CACHE_DIR",
    os.path.join(os.path.dirname(__file__), "..", ".html_cache"),
))
_DEFAULT_TTL = int(os.getenv("CACHE_TTL_SEC", "3600"))  # 1 hour
_write_lock = Lock()


def _path(url: str) -> Path:
    key = hashlib.sha256(url.encode()).hexdigest()
    return _CACHE_DIR / key[:2] / key


def get(url: str, ttl: int = _DEFAULT_TTL) -> str | None:
    """Return cached HTML for *url*, or None on miss/expiry."""
    p = _path(url)
    if not p.exists():
        return None
    try:
        age = time.time() - p.stat().st_mtime
    except OSError:
        return None
    if age > ttl:
        try:
            p.unlink()
        except OSError:
            pass
        return None
    try:
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return None


def put(url: str, html: str) -> None:
    """Store *html* for *url* in the cache."""
    if not html:
        return
    p = _path(url)
    with _write_lock:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(p, "wt", encoding="utf-8") as f:
                f.write(html)
        except Exception:
            pass


def invalidate(url: str) -> None:
    """Remove the cache entry for *url*."""
    try:
        _path(url).unlink()
    except OSError:
        pass


def clear_all() -> int:
    """Remove all cache files. Returns count deleted."""
    removed = 0
    if _CACHE_DIR.exists():
        for f in _CACHE_DIR.rglob("*"):
            if f.is_file():
                try:
                    f.unlink()
                    removed += 1
                except OSError:
                    pass
    return removed
