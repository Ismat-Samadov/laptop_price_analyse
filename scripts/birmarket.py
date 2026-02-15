"""
Scraper for birmarket.az laptops (Nuxt.js SSR).
URL pattern: https://birmarket.az/categories/16-noutbuklar?page={page}
Product data parsed from div.MPProductItem cards in server-rendered HTML.
Last page discovered from pagination links.
Saves all products to data/birmarket.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://birmarket.az"
CATEGORY_URL = f"{BASE_URL}/categories/16-noutbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "birmarket.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "auth.strategy=local; cityId=1; citySelected=true",
    "Referer": BASE_URL,
}

CSV_FIELDS = [
    "product_id",
    "title",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_percent",
    "discount_azn",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for a in soup.select(f'a[href*="categories/16-noutbuklar?page="]'):
        href = a.get("href", "")
        m = re.search(r"page=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(text: str) -> float | None:
    """Convert '1 039.00 ₼' or '749.00 ₼' -> float."""
    if not text:
        return None
    cleaned = text.replace("₼", "").replace("\xa0", "").replace(" ", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.MPProductItem"):
        product_id = card.get("data-product-id", "")

        # --- title ---
        title_el = card.select_one("span.MPTitle")
        title = title_el.get_text(strip=True) if title_el else ""

        # --- URL ---
        link = card.select_one('a[href*="/product/"]')
        url = (BASE_URL + link["href"]) if link and link.get("href") else ""

        # --- prices ---
        price_span = card.select_one("span.flex.flex-col")
        old_span = card.select_one("span.line-through")

        old_price_azn = parse_price(old_span.get_text(strip=True)) if old_span else None

        price_azn = None
        if price_span:
            full_text = price_span.get_text(" ", strip=True)
            old_text = old_span.get_text(strip=True) if old_span else ""
            cur_text = full_text.replace(old_text, "").strip() if old_text else full_text
            price_azn = parse_price(cur_text)

        # --- discount ---
        disc_el = card.select_one(".MPProductItem-Discount")
        discount_percent = disc_el.get_text(strip=True) if disc_el else ""

        discount_azn = None
        if old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_percent": discount_percent,
            "discount_azn": discount_azn,
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
        time.sleep(0.5)
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
