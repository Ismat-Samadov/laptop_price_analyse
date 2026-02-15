"""
Scraper for icomp.az laptops (same custom PHP CMS as compstore.az).
URL pattern: https://icomp.az/kateqoriya/noutbuklar-ultrabuklar.html
             ?action=yes&taxonomy_id=406&taxonomy_page=kateqoriya&s={page}
Product data parsed from div.product cards in server-rendered HTML.
Last page discovered from max s= value in ul.pagination links.
Prices: span.final-price (current) and span.sale-price (original, if discounted).
Saves all products to data/icomp.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://icomp.az"
CATEGORY_URL = (
    f"{BASE_URL}/kateqoriya/noutbuklar-ultrabuklar.html"
    "?action=yes&taxonomy_id=406&taxonomy_page=kateqoriya"
)
OUTPUT = Path(__file__).parent.parent / "data" / "icomp.csv"

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
    "specs",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}&s={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for a in soup.select("ul.pagination a"):
        href = a.get("href", "")
        m = re.search(r"s=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(text: str) -> float | None:
    """Convert plain integer string '3399' -> 3399.0"""
    if not text:
        return None
    cleaned = text.replace(",", "").replace(" ", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product[data-id]"):
        product_id = card.get("data-id", "")

        # --- title & URL ---
        title_el = card.select_one("h3 a")
        title = title_el.get_text(strip=True) if title_el else ""
        url = title_el.get("href", "") if title_el else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # --- prices ---
        final_el = card.select_one("span.final-price")
        sale_el = card.select_one("span.sale-price")

        price_azn = parse_price(final_el.get_text(strip=True)) if final_el else None
        old_price_azn = parse_price(sale_el.get_text(strip=True)) if sale_el else None

        discount_azn = None
        if old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # --- specs / excerpt ---
        specs_el = card.select_one("div.product-excerpt a, div.product-excerpt")
        specs = specs_el.get_text(" ", strip=True) if specs_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
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
