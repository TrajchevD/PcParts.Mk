import logging
import time

log = logging.getLogger("pipeline.scrapers.neptune")

STORE_NAME = "Neptun"

CATEGORIES = {
    "cpu":     "https://www.neptun.mk/Procesori.nspx",
    "gpu":     "https://www.neptun.mk/Graficki_karticki.nspx",
    "ram":     "https://www.neptun.mk/DIMM_(desktop)_memorii.nspx",
    "mb":      "https://www.neptun.mk/Maticni_ploci.nspx",
    "storage": "https://www.neptun.mk/SSD_diskovi.nspx",
}


def _scrape_category(page, category: str, base_url: str) -> list:
    from playwright.sync_api import TimeoutError as PWTimeout

    products = []
    seen = set()
    page_num = 1

    while True:
        url = f"{base_url}?page={page_num}"
        try:
            page.goto(url, timeout=60_000)
            page.wait_for_selector("div.productWrapperInner", timeout=15_000)
        except PWTimeout:
            break

        cards = page.query_selector_all("div.productWrapperInner")
        if not cards:
            break

        new = 0
        for card in cards:
            try:
                title_el = card.query_selector("h2.product-list-item__content--title")
                price_el = card.query_selector("span.priceNum")
                link_el  = card.query_selector("a.theLink")
                if not (title_el and price_el and link_el):
                    continue

                href = link_el.get_attribute("href")
                if not href:
                    continue
                link = "https://www.neptun.mk" + href
                if link in seen:
                    continue
                seen.add(link)
                new += 1

                image = None
                img = card.query_selector(".product-list-item__image img")
                if img:
                    src = img.get_attribute("src") or img.get_attribute("ng-src")
                    if src:
                        image = src if src.startswith("http") else "https://www.neptun.mk/" + src.lstrip("/")

                products.append({
                    "store":    STORE_NAME,
                    "category": category,
                    "title":    title_el.inner_text().strip(),
                    "price":    price_el.inner_text().strip() + " ден.",
                    "link":     link,
                    "image":    image,
                })
            except Exception:
                continue

        if new == 0:
            break
        page_num += 1
        time.sleep(1)

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
