"""
Scraper for brothers.az laptops (custom PHP CMS).
URL: https://brothers.az/product/ucuz-qiymete-notebooklar
All 1500+ products are server-rendered on a single page — no pagination.
Each article.single_product contains duplicate grid/list content sections;
only the grid_content div is parsed to avoid double-counting.
Saves all products to data/brothers.csv.
"""

import csv
import re
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://brothers.az"
LISTING_URL = f"{BASE_URL}/product/ucuz-qiymete-notebooklar"
OUTPUT = Path(__file__).parent.parent / "data" / "brothers.csv"

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
    "label",
]


def fetch_page() -> str:
    req = urllib.request.Request(LISTING_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def parse_price(text: str) -> float | None:
    """Convert '2,219 ₼' or '999 ₼' -> float. Comma is thousands separator."""
    if not text:
        return None
    cleaned = (
        text.replace("₼", "")
            .replace("\xa0", "")
            .replace(",", "")   # thousands separator
            .replace(" ", "")
            .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("article.single_product"):
        # --- URL & product ID ---
        link = card.select_one("a.primary_img")
        url = link.get("href", "") if link else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # Extract ID from URL path: /product_read/{id}/slug
        pid_m = re.search(r"/product_read/(\d+)/", url)
        product_id = pid_m.group(1) if pid_m else ""

        # --- title (grid section only to avoid duplication) ---
        title_el = card.select_one("div.grid_content h3.product_name a")
        if not title_el:
            title_el = card.select_one("h3.product_name a")
        title = title_el.get_text(strip=True) if title_el else ""

        # --- price (grid section only) ---
        price_el = card.select_one("div.grid_content span.current_price")
        if not price_el:
            price_el = card.select_one("span.current_price")
        price_azn = parse_price(price_el.get_text(strip=True)) if price_el else None

        # --- label (e.g. "Yeni") ---
        label_el = card.select_one("div.label_product span.label_sale")
        label = label_el.get_text(strip=True) if label_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "label": label,
        })

    return products


def save_csv(products: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(products)
    print(f"Saved {len(products)} rows -> {path}")


if __name__ == "__main__":
    print(f"Fetching {LISTING_URL} (single large page) ...")
    html = fetch_page()
    print("  Parsing products ...")
    products = parse_products(html)
    print(f"  Found {len(products)} products")
    save_csv(products, OUTPUT)
