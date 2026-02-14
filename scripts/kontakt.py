"""
Scraper for kontakt.az laptops.
URL pattern: https://kontakt.az/notbuk-ve-kompyuterler/komputerler/notbuklar?p={page}
Saves all products to data/kontakt.csv.
"""

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://kontakt.az"
CATEGORY_URL = f"{BASE_URL}/notbuk-ve-kompyuterler/komputerler/notbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "kontakt.csv"

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
    "sku",
    "title",
    "brand",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "specs",
    "category",
    "category2",
    "category3",
]


def parse_price(text: str) -> float | None:
    """Convert '1.799,99 ₼' -> 1799.99"""
    if not text:
        return None
    cleaned = text.replace("₼", "").replace("\xa0", "").strip()
    # Azerbaijani format: thousands sep = '.', decimal sep = ','
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}?p={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    """Return the last page number from pagination."""
    page_links = soup.select(".pages-items .item a")
    max_page = 1
    for link in page_links:
        href = link.get("href", "")
        m = re.search(r"[?&]p=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product-item"):
        # --- GTM data (most fields) ---
        gtm_raw = card.get("data-gtm", "{}")
        try:
            gtm = json.loads(gtm_raw)
        except json.JSONDecodeError:
            gtm = {}

        product_id = card.get("id", "")
        sku = card.get("data-sku", "")
        title = gtm.get("item_name", "")
        brand = gtm.get("item_brand", "")
        price_gtm = gtm.get("price")          # current price from GTM
        discount_gtm = gtm.get("discount")    # discount amount from GTM
        category = gtm.get("item_category", "")
        category2 = gtm.get("item_category2", "")
        category3 = gtm.get("item_category3", "")

        # --- URL ---
        img_link = card.select_one("a.prodItem__img")
        url = img_link["href"] if img_link and img_link.get("href") else ""

        # --- Prices from DOM (more reliable display values) ---
        prices_div = card.select_one(".prodItem__prices")
        old_price_azn = None
        price_azn = None
        if prices_div:
            old_tag = prices_div.select_one("i")
            cur_tag = prices_div.select_one("b")
            if old_tag:
                old_price_azn = parse_price(old_tag.get_text(strip=True))
            if cur_tag:
                price_azn = parse_price(cur_tag.get_text(strip=True))

        # Fallback to GTM price if DOM parsing fails
        if price_azn is None and price_gtm is not None:
            try:
                price_azn = float(price_gtm)
            except (ValueError, TypeError):
                pass

        # Discount: prefer GTM value, else compute from prices
        discount_azn = None
        if discount_gtm is not None:
            try:
                discount_azn = float(discount_gtm)
            except (ValueError, TypeError):
                pass
        elif old_price_azn and price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # --- Specs ---
        specs_el = card.select_one(".prodItem__wrapText")
        specs = specs_el.get_text(" ", strip=True) if specs_el else ""

        products.append({
            "product_id": product_id,
            "sku": sku,
            "title": title,
            "brand": brand,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "specs": specs,
            "category": category,
            "category2": category2,
            "category3": category3,
        })

    return products


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {CATEGORY_URL}")

    # Fetch page 1 to determine last page
    print("  Fetching page 1 (discovering pagination) ...", end=" ", flush=True)
    html = fetch_page(1)
    soup = BeautifulSoup(html, "html.parser")
    last_page = get_last_page(soup)
    print(f"last page = {last_page}")

    all_products: list[dict] = []

    # Parse page 1 we already fetched
    page_products = parse_products(html)
    all_products.extend(page_products)
    print(f"  Page 1: {len(page_products)} products  (total: {len(all_products)})")

    # Fetch remaining pages
    for page in range(2, last_page + 1):
        time.sleep(0.6)  # polite delay
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
