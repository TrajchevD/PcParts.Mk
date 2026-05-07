"""Temporary investigation script — renders Setec/Neptun pages and dumps spec HTML."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

PAGES = {
    "setec":  "https://www.setec.mk/products/cpu-amd-ryzen-5-5500-tray",
    "neptun": "https://www.neptun.mk/categories/procesori/84119506-CPU-AMD-Ryzen-7-9850X3D-6-Core-4-7GHz-96MB-Cache-AM5-w-o-Cooler-BOX",
}

KEYWORDS = ["spec", "desc", "attr", "detail", "param", "charact", "info", "tab", "product"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for name, url in PAGES.items():
        print(f"\n{'='*60}")
        print(f"  {name.upper()}  —  {url}")
        print(f"{'='*60}")
        try:
            page.goto(url, timeout=35_000)
            page.wait_for_load_state("networkidle", timeout=20_000)
        except Exception as e:
            print(f"  Load error: {e}")

        html  = page.content()
        soup  = BeautifulSoup(html, "html.parser")

        # 1. Print full text of any element whose id/class matches keywords
        seen = set()
        for tag in soup.find_all(True):
            tag_id  = (tag.get("id") or "").lower()
            tag_cls = " ".join(tag.get("class") or []).lower()
            for kw in KEYWORDS:
                if kw in tag_id or kw in tag_cls:
                    key = f"{tag.name}|{tag_id}|{tag_cls[:50]}"
                    if key not in seen:
                        seen.add(key)
                        txt = tag.get_text(separator=" | ", strip=True)
                        if len(txt) > 30:   # skip empty/nav tags
                            print(f"\n  TAG: <{tag.name} id='{tag.get('id')}' class='{tag.get('class')}'>")
                            print(f"  TEXT: {txt[:600]}")
                    break

        # 2. Dump all tables
        tables = soup.find_all("table")
        print(f"\n  Tables: {len(tables)}")
        for i, t in enumerate(tables[:3]):
            print(f"  Table {i}: {t.get_text(separator=' | ', strip=True)[:400]}")

        # 3. Dump all <dl> (definition lists) — common for specs
        dls = soup.find_all("dl")
        print(f"\n  DL elements: {len(dls)}")
        for i, dl in enumerate(dls[:3]):
            print(f"  DL {i}: {dl.get_text(separator=' | ', strip=True)[:400]}")

        # 4. Dump full text of page (truncated) to scan for spec keywords
        full_text = soup.get_text(separator="\n", strip=True)
        lines = [l for l in full_text.splitlines() if len(l.strip()) > 3]
        # Find lines near "socket", "cores", "GHz", "TDP"
        spec_terms = ["socket", "core", "thread", "ghz", "tdp", "watt", "mhz", "ddr", "pcie", "vram", "memory"]
        print(f"\n  Spec-related lines from page text:")
        for i, line in enumerate(lines):
            if any(t in line.lower() for t in spec_terms):
                context = lines[max(0,i-1):i+3]
                for c in context:
                    print(f"    {c}")
                print()

    browser.close()
