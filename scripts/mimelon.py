"""
Scraper for mimelon.com laptops (custom CodeIgniter CMS).
URL pattern:
  Page 1: https://mimelon.com/az/notebooklar
  Page N: https://mimelon.com/az/notebooklar/{N}
Product data parsed from div.product.owl-item-slide cards (template card excluded).
Last page discovered from max data-ci-pagination-page in div.pagination.main-pagination.
Price: span.product-caption-price-new contains "979m" — 'm' is the AZN icon; stripped via regex.
Saves all products to data/mimelon.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://mimelon.com"
CATEGORY_URL = f"{BASE_URL}/az/notebooklar"
OUTPUT = Path(__file__).parent.parent / "data" / "mimelon.csv"

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


def fetch_page(page: int) -> str:
    url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}/{page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    pag = soup.select_one("div.pagination.main-pagination")
    if pag:
        for a in pag.select("a[data-ci-pagination-page]"):
            p = a.get("data-ci-pagination-page", "")
            if p.isdigit():
                max_page = max(max_page, int(p))
    return max_page


def parse_price(text: str) -> float | None:
    """Extract numeric price from '979m', '1 299m', '2,199m' -> float."""
    if not text:
        return None
    # Keep only digits, spaces, commas, dots; then clean up
    cleaned = re.sub(r"[^\d\s,\.]", "", text).strip()
    cleaned = cleaned.replace(" ", "").replace(",", ".")
    # Handle double dots from bad data
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = parts[0] + "." + "".join(parts[1:])
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product.owl-item-slide"):
        # Skip the JS template placeholder card
        classes = card.get("class", [])
        if "hide" in classes or "product_example" in classes:
            continue

        # --- product ID & URL ---
        link = card.select_one("a.dataLayerProductClick")
        product_id = link.get("data-id", "") if link else ""
        url = link.get("href", "") if link else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # --- title ---
        title_el = card.select_one("h5.product-caption-title")
        title = title_el.get_text(strip=True) if title_el else ""

        # --- price ---
        price_el = card.select_one("span.product-caption-price-new")
        price_azn = parse_price(price_el.get_text(strip=True)) if price_el else None

        # --- label (e.g. 'Out of stock', sale badge) ---
        label_el = card.select_one("div.product-label")
        label = label_el.get_text(strip=True) if label_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "label": label,
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
