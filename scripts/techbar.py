"""
Scraper for techbar.az laptops (WooCommerce).
URL pattern: https://techbar.az/noutbuklar/page/{page}/
Last page discovered from a.page-numbers links.
Saves all products to data/techbar.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://techbar.az"
CATEGORY_URL = f"{BASE_URL}/noutbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "techbar.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
}

CSV_FIELDS = [
    "product_id",
    "title",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "labels",
    "specs",
]


def fetch_page(page: int) -> str:
    url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}/page/{page}/"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for a in soup.select("a.page-numbers"):
        href = a.get("href", "")
        m = re.search(r"/page/(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(bdi_el) -> float | None:
    """Parse price from <bdi> element, e.g. '2,279.00 ₼' -> 2279.00"""
    if not bdi_el:
        return None
    # Get text, strip currency symbol, remove thousands comma
    text = bdi_el.get_text(strip=True)
    text = text.replace("₼", "").replace("\xa0", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.wd-product[data-id]"):
        product_id = card.get("data-id", "")

        # --- title & URL ---
        title_el = card.select_one("h2.woocommerce-loop-product__title")
        title = title_el.get_text(strip=True) if title_el else ""

        link = card.select_one("a.product-image-link, a.woocommerce-loop-product__link")
        url = link.get("href", "") if link else ""

        # --- prices (WooCommerce del/ins pattern) ---
        old_price_azn = None
        price_azn = None

        del_el = card.select_one("del .woocommerce-Price-amount bdi")
        ins_el = card.select_one("ins .woocommerce-Price-amount bdi")

        if del_el:
            old_price_azn = parse_price(del_el)
        if ins_el:
            price_azn = parse_price(ins_el)

        # No discount — single price
        if price_azn is None:
            single = card.select_one(".woocommerce-Price-amount bdi")
            price_azn = parse_price(single)

        discount_azn = None
        if old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # --- labels ---
        label_els = card.select(".product-label")
        labels = " | ".join(l.get_text(strip=True) for l in label_els if l.get_text(strip=True))

        # --- short specs (description excerpt if present) ---
        specs_el = card.select_one(".wd-desc, .short-description, .product-excerpt, [class*=spec]")
        specs = specs_el.get_text(" ", strip=True) if specs_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "labels": labels,
            "specs": specs,
        })

    return products


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {CATEGORY_URL}")

    print("  Fetching page 1 (discovering pagination) ...", end=" ", flush=True)
    html = fetch_page(1)
    soup = BeautifulSoup(html, "html.parser")
    last_page = get_last_page(soup)
    print(f"last page = {last_page}")

    all_products: list[dict] = []

    page_products = parse_products(html)
    all_products.extend(page_products)
    print(f"  Page 1: {len(page_products)} products  (total: {len(all_products)})")

    for page in range(2, last_page + 1):
        time.sleep(0.6)
        print(f"  Fetching page {page}/{last_page} ...", end=" ", flush=True)
        html = fetch_page(page)
        page_products = parse_products(html)
        all_products.extend(page_products)
        print(f"got {len(page_products)} products  (total: {len(all_products)})")

    return all_products


def save_csv(products: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(products)
    print(f"\nSaved {len(products)} rows -> {path}")


if __name__ == "__main__":
    products = scrape_all()
    save_csv(products, OUTPUT)
