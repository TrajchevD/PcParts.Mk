import logging
import time
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("pipeline.scrapers.gjirafa")

STORE_NAME = "Gjirafa50"

CATEGORIES = {
    "cpu":     "https://gjirafa50.mk/procesor?pagenumber=",
    "gpu":     "https://gjirafa50.mk/grafichka-karta-kompjuterski-delovi?pagenumber=",
    "ram":     "https://gjirafa50.mk/operativna-memorija-kompjuterski-delovi?pagenumber=",
    "mb":      "https://gjirafa50.mk/matichna-plocha-kompjuterski-delovi?pagenumber=",
    "storage": "https://gjirafa50.mk/disk?pagenumber=",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _scrape_category(category: str, base_url: str) -> list:
    products = []
    seen = set()
    page = 1

    while True:
        url = f"{base_url}{page}&orderby=&hls=false&is=true"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
        except Exception as exc:
            log.warning(f"[{category}] page {page} failed: {exc}")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("div.item-box")
        if not cards:
            break

        new = 0
        for card in cards:
            title_el = card.select_one("h3.product-title a")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            href  = title_el.get("href", "")
            link  = "https://gjirafa50.mk" + href
            if link in seen:
                continue
            seen.add(link)
            new += 1

            img_el = card.select_one("section.picture img")
            image = None
            if img_el:
                src = img_el.get("src") or img_el.get("data-src")
                if src:
                    image = src if src.startswith("http") else "https://gjirafa50.mk" + src

            price_el = card.select_one("span.price")
            price = price_el.get_text(strip=True).replace("MKD.", "MKD").strip() if price_el else ""

            products.append({
                "store":    STORE_NAME,
                "category": category,
                "title":    title,
                "price":    price,
                "link":     link,
                "image":    image,
            })

        if new == 0:
            break
        page += 1
        time.sleep(1)

    log.info(f"[{category}] {len(products)} products")
    return products


def run() -> list:
    all_products = []
    for category, base_url in CATEGORIES.items():
        all_products.extend(_scrape_category(category, base_url))
    log.info(f"Total: {len(all_products)}")
    return all_products
