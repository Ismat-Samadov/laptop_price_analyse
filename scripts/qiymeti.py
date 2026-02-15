"""
Scraper for qiymeti.net laptops (WordPress custom AJAX).
Endpoint: GET https://qiymeti.net/wp-admin/admin-ajax.php
Params: sehife={page}&action=print_filters_and_products&product_type=notebook
Returns HTML fragment with product cards + pagination.
Last page parsed from div.pagination page-numbers text (max numeric value).
28 products per page, ~506 total across 19 pages.
Saves all products to data/qiymeti.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://qiymeti.net"
AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"
OUTPUT = Path(__file__).parent.parent / "data" / "qiymeti.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/qiymetleri/notebook/",
    "DNT": "1",
}

CSV_FIELDS = [
    "product_id",
    "title",
    "url",
    "price_azn",
    "specs",
]


def fetch_page(page: int) -> str:
    url = (
        f"{AJAX_URL}?sehife={page}"
        "&action=print_filters_and_products"
        "&product_type=notebook"
    )
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for el in soup.select("div.pagination a.page-numbers, div.pagination span.page-numbers"):
        txt = el.get_text(strip=True)
        if txt.isdigit():
            max_page = max(max_page, int(txt))
    return max_page


def parse_price(text: str) -> float | None:
    """Convert '1 239 ,00 AZN' or '2 993,00 AZN' -> float.
    Space is thousands separator; comma is decimal separator.
    """
    if not text:
        return None
    cleaned = (
        text.replace("AZN", "")
            .replace("\xa0", "")
            .replace(" ", "")
            .strip()
    )
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> tuple[list[dict], BeautifulSoup]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product[data-product-id]"):
        product_id = card.get("data-product-id", "")

        # --- title & URL ---
        title_el = card.select_one("div.name a")
        title = title_el.get_text(strip=True) if title_el else ""

        link = card.select_one("div.thumbnail a") or card.select_one("div.name a")
        url = link.get("href", "") if link else ""

        # --- price ---
        price_el = card.select_one("div.min-price")
        price_azn = parse_price(price_el.get_text(" ", strip=True)) if price_el else None

        # --- specs ---
        specs_el = card.select_one("div.specifications")
        specs = specs_el.get_text(strip=True) if specs_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "specs": specs,
        })

    return products, soup


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {AJAX_URL}")

    print("  Fetching page 1 (discovering pagination) ...", end=" ", flush=True)
    html = fetch_page(1)
    page_products, soup = parse_products(html)
    last_page = get_last_page(soup)
    print(f"last page = {last_page}")

    all_products: list[dict] = []
    all_products.extend(page_products)
    print(f"  Page 1: {len(page_products)} products  (total: {len(all_products)})")

    for page in range(2, last_page + 1):
        time.sleep(0.5)
        print(f"  Fetching page {page}/{last_page} ...", end=" ", flush=True)
        html = fetch_page(page)
        page_products, _ = parse_products(html)
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
