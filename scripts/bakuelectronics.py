"""
Scraper for bakuelectronics.az laptops.
URL pattern: https://www.bakuelectronics.az/catalog/noutbuklar-komputerler-planshetler/noutbuklar?page={page}
Product data is embedded in __NEXT_DATA__ JSON — no JS rendering needed.
Saves all products to data/bakuelectronics.csv.
"""

import csv
import json
import math
import re
import time
import urllib.request
from pathlib import Path

BASE_URL = "https://www.bakuelectronics.az"
CATEGORY_URL = f"{BASE_URL}/catalog/noutbuklar-komputerler-planshetler/noutbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "bakuelectronics.csv"

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
    "product_code",
    "title",
    "url",
    "price_azn",
    "discounted_price_azn",
    "discount_azn",
    "monthly_payment_azn",
    "installment_months",
    "rating",
    "review_count",
    "quantity",
    "is_online",
]


def fetch_page_json(page: int) -> dict:
    url = f"{CATEGORY_URL}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")

    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not m:
        return {}
    return json.loads(m.group(1))


def parse_products(next_data: dict) -> tuple[list[dict], int, int]:
    """Return (products, total, size)."""
    try:
        inner = next_data["props"]["pageProps"]["products"]["products"]
    except (KeyError, TypeError):
        return [], 0, 18

    items = inner.get("items", [])
    total = inner.get("total", 0)
    size = inner.get("size", 18)

    products = []
    for item in items:
        per_month = item.get("perMonth") or {}
        monthly_price = per_month.get("price")
        installment_months = per_month.get("month")

        slug = item.get("slug", "")
        url = f"{BASE_URL}/mehsul/{slug}" if slug else ""

        # Prices
        price_azn = item.get("price")
        discounted_price = item.get("discounted_price")
        discount_raw = item.get("discount", 0)
        try:
            discount_azn = float(discount_raw) if discount_raw else None
        except (ValueError, TypeError):
            discount_azn = None

        # If no discount, selling price = original price
        if not discounted_price or discounted_price == price_azn:
            discounted_price = price_azn
            discount_azn = None

        products.append({
            "product_id": item.get("id", ""),
            "product_code": item.get("product_code", ""),
            "title": item.get("name", ""),
            "url": url,
            "price_azn": price_azn,
            "discounted_price_azn": discounted_price,
            "discount_azn": discount_azn,
            "monthly_payment_azn": monthly_price,
            "installment_months": installment_months,
            "rating": item.get("rate", ""),
            "review_count": item.get("reviewCount", ""),
            "quantity": item.get("quantity", ""),
            "is_online": item.get("is_online", ""),
        })

    return products, total, size


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {CATEGORY_URL}")

    print("  Fetching page 1 (discovering pagination) ...", end=" ", flush=True)
    next_data = fetch_page_json(1)
    page_products, total, size = parse_products(next_data)
    last_page = math.ceil(total / size) if size else 1
    print(f"total={total}  size={size}  last_page={last_page}")

    all_products: list[dict] = []
    all_products.extend(page_products)
    print(f"  Page 1: {len(page_products)} products  (total: {len(all_products)})")

    for page in range(2, last_page + 1):
        time.sleep(0.5)
        print(f"  Fetching page {page}/{last_page} ...", end=" ", flush=True)
        next_data = fetch_page_json(page)
        page_products, _, _ = parse_products(next_data)
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
