import logging
import time
import requests

log = logging.getLogger("pipeline.scrapers.anhoch")

STORE_NAME = "Anhoch"

CATEGORY_URLS = {
    "cpu":     "https://www.anhoch.com/products?categories[0]=procesori&inStockOnly=1&sort=latest&perPage=20&page=",
    "gpu":     "https://www.anhoch.com/products?categories[0]=grafichki-karti&inStockOnly=1&sort=latest&perPage=20&page=",
    "ram":     "https://www.anhoch.com/products?categories[0]=desktop-ram-memorii&inStockOnly=1&sort=latest&perPage=20&page=",
    "mb":      "https://www.anhoch.com/products?categories[0]=matichni-plochi&inStockOnly=1&sort=latest&perPage=20&page=",
    "storage": "https://www.anhoch.com/products?categories[0]=diskovi-i-skladiranje&inStockOnly=1&sort=latest&perPage=20&page=",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept":     "application/json",
}


def _fetch_page(base_url: str, page: int) -> list:
    try:
        r = requests.get(f"{base_url}{page}", headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("products", {}).get("data", [])
    except Exception as exc:
        log.warning(f"Page {page} failed: {exc}")
        return []


def _parse_item(item: dict, category: str) -> dict | None:
    title = item.get("name")
    slug  = item.get("slug")
    price = item.get("price", {}).get("formatted")
    if not (title and slug and price):
        return None

    image = None
    base_image = item.get("base_image")
    if isinstance(base_image, dict):
        image = base_image.get("path")
    elif isinstance(base_image, list) and base_image:
        image = base_image[0].get("path")
    if image and not image.startswith("http"):
        image = "https://www.anhoch.com" + image

    return {
        "store":    STORE_NAME,
        "category": category,
        "title":    title,
        "price":    price,
        "link":     f"https://www.anhoch.com/products/{slug}",
        "image":    image,
    }


def _scrape_category(category: str, base_url: str) -> list:
    products = []
    page = 1
    while True:
        items = _fetch_page(base_url, page)
        if not items:
            break
        for item in items:
            parsed = _parse_item(item, category)
            if parsed:
                products.append(parsed)
        page += 1
        time.sleep(0.5)
    log.info(f"[{category}] {len(products)} products")
    return products


def run() -> list:
    all_products = []
    for category, base_url in CATEGORY_URLS.items():
        all_products.extend(_scrape_category(category, base_url))
    log.info(f"Total: {len(all_products)}")
    return all_products
