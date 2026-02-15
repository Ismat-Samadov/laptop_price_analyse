"""
Scraper for mgstore.az laptops.
URL pattern: https://mgstore.az/notbuk-ve-kompyuterler/kompyuterler/notbuklar?p={page}
Same Magento structure as kontakt.az — data-gtm JSON + prodItem__prices.
Saves all products to data/mgstore.csv.
"""

import csv
import json
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://mgstore.az"
CATEGORY_URL = f"{BASE_URL}/notbuk-ve-kompyuterler/kompyuterler/notbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "mgstore.csv"

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
    """Convert '2.399,99 ₼' -> 2399.99"""
    if not text:
        return None
    cleaned = text.replace("₼", "").replace("\xa0", "").strip()
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
    max_page = 1
    for link in soup.select(".pages-items .item a"):
        href = link.get("href", "")
        m = re.search(r"[?&]p=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product-item"):
        gtm_raw = card.get("data-gtm", "{}")
        try:
            gtm = json.loads(gtm_raw)
        except json.JSONDecodeError:
            gtm = {}

        product_id = card.get("id", "")
        sku = card.get("data-sku", "")
        title = gtm.get("item_name", "")
        brand = gtm.get("item_brand", "")
        category = gtm.get("item_category", "")
        category2 = gtm.get("item_category2", "")
        category3 = gtm.get("item_category3", "")

        img_link = card.select_one("a.prodItem__img")
        url = img_link["href"] if img_link and img_link.get("href") else ""

        # Prices from DOM
        prices_div = card.select_one(".prodItem__prices")
        old_price_azn = None
        price_azn = None
        discount_azn = None

        if prices_div:
            old_tag = prices_div.select_one("i")
            cur_tag = prices_div.select_one("b")
            if old_tag:
                old_price_azn = parse_price(old_tag.get_text(strip=True))
            if cur_tag:
                price_azn = parse_price(cur_tag.get_text(strip=True))

        # Fallback to GTM price
        if price_azn is None:
            try:
                price_azn = float(gtm.get("price", 0) or 0) or None
            except (ValueError, TypeError):
                pass

        # Discount
        try:
            disc = float(gtm.get("discount", 0) or 0)
            discount_azn = disc if disc else None
        except (ValueError, TypeError):
            pass

        if discount_azn is None and old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # Specs
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
