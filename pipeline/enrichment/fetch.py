"""
Unified spec-text fetcher for enrichment parsers.

Strategy per store:
  - anhoch.com   → HTTP + div#description  (fallbacks: class-based selectors)
  - gjirafa50.mk → HTTP + #product-specifications-split-page + #product-desc
  - neptun.mk    → HTTP static attempt first, then Playwright (AngularJS)
  - setec.mk     → HTTP static + __NEXT_DATA__ JSON extraction + Playwright fallback

All HTTP fetches use an in-memory + disk cache and exponential-backoff retry.
Playwright instances are limited by a global semaphore to avoid OOM.
"""
import json
import re
import time
import threading
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from enrichment.cache import get as _cache_get, put as _cache_put

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# At most 4 concurrent headless browser instances across all threads
_PLAYWRIGHT_SEM = threading.Semaphore(4)

_MAX_RETRIES = 3
_RETRY_BASE  = 2.0   # delay = _RETRY_BASE ** attempt  (2s, 4s, 8s)


# ── Shared HTTP helpers ──────────────────────────────────────────────────────

def _get_html(url: str, use_cache: bool = True) -> str | None:
    """Fetch URL with caching and exponential-backoff retry. Returns raw HTML."""
    if use_cache:
        cached = _cache_get(url)
        if cached:
            return cached

    for attempt in range(_MAX_RETRIES):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                html = r.text
                if use_cache and html:
                    _cache_put(url, html)
                return html
            if r.status_code in (429, 502, 503):
                time.sleep(_RETRY_BASE ** (attempt + 1))
                continue
            return None  # 404, 403, etc. — won't improve with retry
        except (requests.ConnectionError, requests.Timeout):
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BASE ** (attempt + 1))
    return None


# ── Public entry point ───────────────────────────────────────────────────────

def fetch_spec_text(url: str, use_cache: bool = True) -> str | None:
    if not url:
        return None
    domain = urlparse(url).netloc.lower()
    if "neptun.mk" in domain:
        return _fetch_neptun(url, use_cache)
    if "setec.mk" in domain:
        return _fetch_setec(url, use_cache)
    if "gjirafa50" in domain:
        return _fetch_gjirafa(url, use_cache)
    return _fetch_anhoch(url, use_cache)


# ── Anhoch ───────────────────────────────────────────────────────────────────

def _fetch_anhoch(url: str, use_cache: bool = True) -> str | None:
    html = _get_html(url, use_cache)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    # Primary: div#description
    div = soup.find("div", id="description")
    if not div:
        # Fallback: any div whose class contains "description"
        div = soup.find("div", class_=lambda c: c and "description" in " ".join(c).lower())
    if not div:
        div = soup.find("div", class_=lambda c: c and "product-spec" in " ".join(c or []).lower())
    if not div:
        return None
    return div.get_text(separator=" ", strip=True).replace("\xa0", " ")


# ── Gjirafa50 ────────────────────────────────────────────────────────────────

def _fetch_gjirafa(url: str, use_cache: bool = True) -> str | None:
    html = _get_html(url, use_cache)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    parts: list[str] = []

    spec_el = soup.find(id="product-specifications-split-page")
    if spec_el:
        parts.append(spec_el.get_text(separator=" ", strip=True))

    desc_el = soup.find(id="product-desc")
    if desc_el:
        txt = desc_el.get_text(separator=" ", strip=True)
        if len(txt) > 80 and "обработува" not in txt:
            parts.append(txt)

    if not parts:
        # Broad fallback: any element with "specification" or "attributes" in id/class
        for tag in soup.find_all(True):
            tag_id  = (tag.get("id") or "").lower()
            tag_cls = " ".join(tag.get("class") or []).lower()
            if "specification" in tag_id or "specification" in tag_cls \
               or "attributes" in tag_id or "attributes" in tag_cls:
                t = tag.get_text(separator=" ", strip=True)
                if len(t) > 50:
                    parts.append(t)
                    break

    return " ".join(parts).replace("\xa0", " ") or None


# ── Setec (Next.js) ──────────────────────────────────────────────────────────

_SETEC_SELECTORS = [
    lambda s: s.find("div", class_=lambda c: c and "specification" in " ".join(c or []).lower()),
    lambda s: s.find("div", class_=lambda c: c and "product-detail" in " ".join(c or []).lower()),
    lambda s: s.find("ul",  class_=lambda c: c and "spec" in " ".join(c or []).lower()),
    lambda s: s.find("table", class_=lambda c: "spec" in " ".join(c or []).lower()),
    lambda s: s.find("dl"),
    lambda s: s.find("div", attrs={"data-testid": "product-specifications"}),
    lambda s: s.find("div", attrs={"data-testid": "specifications"}),
]


def _extract_next_data(soup: BeautifulSoup) -> str | None:
    """Flatten Next.js __NEXT_DATA__ JSON into key:value spec text."""
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    try:
        data = json.loads(script.string)
    except (json.JSONDecodeError, ValueError):
        return None

    parts: list[str] = []
    _flatten(data, parts, depth=0, max_depth=12)
    text = " ".join(parts)

    spec_terms = ("socket", "core", "ghz", "tdp", "ddr", "mhz",
                  "nvme", "sata", "vram", "pcie", "gb", "interface")
    if any(t in text.lower() for t in spec_terms):
        return text
    return None


def _flatten(obj, parts: list, depth: int, max_depth: int) -> None:
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int, float)) and v:
                parts.append(f"{k}: {v}")
            else:
                _flatten(v, parts, depth + 1, max_depth)
    elif isinstance(obj, list):
        for item in obj:
            _flatten(item, parts, depth + 1, max_depth)


def _apply_setec_selectors(soup: BeautifulSoup) -> str | None:
    for fn in _SETEC_SELECTORS:
        try:
            el = fn(soup)
            if el:
                t = el.get_text(separator=" ", strip=True).replace("\xa0", " ")
                if len(t) > 50:
                    return t
        except Exception:
            continue
    return None


def _fetch_setec(url: str, use_cache: bool = True) -> str | None:
    """
    Three-stage strategy for Next.js Setec pages:
      1. Static HTML → __NEXT_DATA__ JSON extraction
      2. Static HTML → selector-based parse (SSR content)
      3. Playwright fallback → full render + selectors + spec-line extraction
    """
    html = _get_html(url, use_cache)
    if html:
        soup = BeautifulSoup(html, "html.parser")

        text = _extract_next_data(soup)
        if text:
            return text

        text = _apply_setec_selectors(soup)
        if text:
            return text

    return _fetch_setec_playwright(url)


def _fetch_setec_playwright(url: str) -> str | None:
    with _PLAYWRIGHT_SEM:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context()
                ctx.route(
                    "**/*",
                    lambda r: r.abort()
                    if r.request.resource_type in ("font", "media", "image", "stylesheet")
                    else r.continue_(),
                )
                page = ctx.new_page()
                page.goto(url, timeout=35_000)
                page.wait_for_load_state("networkidle", timeout=20_000)
                rendered = page.content()
                browser.close()
        except Exception:
            return None

    soup = BeautifulSoup(rendered, "html.parser")

    text = _apply_setec_selectors(soup)
    if text:
        return text

    # Last resort: extract lines that contain spec-related keywords
    spec_terms = ("socket", "core", "ghz", "tdp", "ddr", "mhz",
                  "nvme", "sata", "vram", "pcie", "gb", "interface", "rpm")
    lines = [
        ln.strip()
        for ln in soup.get_text(separator="\n", strip=True).splitlines()
        if any(t in ln.lower() for t in spec_terms) and len(ln.strip()) > 5
    ]
    return "\n".join(lines) or None


# ── Neptun (AngularJS) ───────────────────────────────────────────────────────

def _fetch_neptun(url: str, use_cache: bool = True) -> str | None:
    # Try static HTML first — Neptun occasionally serves SSR content
    html = _get_html(url, use_cache)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find(id="productSpecification")
        if div:
            t = div.get_text(separator=" ", strip=True)
            if len(t) > 50:
                return t

    # Playwright for AngularJS-rendered pages
    with _PLAYWRIGHT_SEM:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context()
                ctx.route(
                    "**/*",
                    lambda r: r.abort()
                    if r.request.resource_type in ("font", "media", "image", "stylesheet")
                    else r.continue_(),
                )
                page = ctx.new_page()
                page.goto(url, timeout=35_000)
                page.wait_for_load_state("networkidle", timeout=20_000)
                rendered = page.content()
                browser.close()
        except Exception:
            return None

    if use_cache:
        _cache_put(url, rendered)

    soup = BeautifulSoup(rendered, "html.parser")

    div = soup.find(id="productSpecification")
    if div:
        return div.get_text(separator=" ", strip=True)

    # Fallback selectors on rendered HTML
    for fn in [
        lambda s: s.find("div", class_=lambda c: c and "specification" in " ".join(c or []).lower()),
        lambda s: s.find("table", class_=lambda c: "spec" in " ".join(c or []).lower()),
        lambda s: s.find("dl"),
    ]:
        try:
            el = fn(soup)
            if el:
                t = el.get_text(separator=" ", strip=True)
                if len(t) > 50:
                    return t
        except Exception:
            continue

    return None
