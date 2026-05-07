import logging
from urllib.parse import urlparse, parse_qs, unquote

log = logging.getLogger("pipeline.scrapers.setec")

STORE_NAME = "Setec"

CATEGORIES = {
    "cpu":     "https://www.setec.mk/category/protsesori-21",
    "gpu":     "https://www.setec.mk/category/grafichki-20karti-25",
    "ram":     "https://www.setec.mk/category/ram-20memori-d1-98a-24",
    "mb":      "https://www.setec.mk/category/matichni-20plochi-22",
    "storage": "https://www.setec.mk/category/tvrdi-20diskovi-20i-20ssd-20diskovi-23",
}


def _decode_image(card) -> str | None:
    img = card.query_selector("div.relative.mb-4 > img")
    if not img:
        return None
    src = img.get_attribute("src")
    if not src:
        return None
    if src.startswith("/_next/image"):
        qs = parse_qs(urlparse(src).query)
        decoded = unquote(qs["url"][0]) if "url" in qs else None
    else:
        decoded = src
    if decoded and "empty.webp" in decoded:
        return None
    return decoded


def _scrape_category(page, category: str, base_url: str) -> list:
    products = []
    page_num = 1

    while True:
        url = f"{base_url}?page={page_num}"
        try:
            page.goto(url, timeout=45_000)
            page.wait_for_selector("div.grid", timeout=15_000)
        except Exception:
            break

        cards = page.query_selector_all("div.relative.bg-white")
        if not cards:
            break

        found = 0
        for card in cards:
            if card.query_selector("span:has-text('Топ зделка')"):
                continue
            title_el = card.query_selector("h3")
            link_el  = card.query_selector("a[href]")
            price_el = card.query_selector("p.text-orange span.text-xl")
            if not (title_el and link_el and price_el):
                continue

            link = link_el.get_attribute("href")
            if link and link.startswith("/"):
                link = "https://www.setec.mk" + link

            products.append({
                "store":    STORE_NAME,
                "category": category,
                "title":    title_el.inner_text().strip(),
                "price":    price_el.inner_text().strip(),
                "link":     link,
                "image":    _decode_image(card),
            })
            found += 1

        if found == 0:
            break
        page_num += 1

    log.info(f"[{category}] {len(products)} products")
    return products


def run() -> list:
    from playwright.sync_api import sync_playwright

    all_products = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        ctx.route("**/*", lambda r: r.abort()
                  if r.request.resource_type in ("font", "media") else r.continue_())
        page = ctx.new_page()

        for category, url in CATEGORIES.items():
            all_products.extend(_scrape_category(page, category, url))

        browser.close()

    log.info(f"Total: {len(all_products)}")
    return all_products
