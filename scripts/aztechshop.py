"""
Scraper for aztechshop.az laptops.
URL pattern: https://aztechshop.az/noutbuklar/?page={page}
Saves all products to data/aztechshop.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://aztechshop.az"
CATEGORY_URL = f"{BASE_URL}/noutbuklar/"
OUTPUT = Path(__file__).parent.parent / "data" / "aztechshop.csv"

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
    "description",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "availability",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    """Return last page number from the '>|' (last) pagination link."""
    pager = soup.select_one("ul.pagination")
    if not pager:
        return 1
    max_page = 1
    for link in pager.select("a"):
        href = link.get("href", "")
        m = re.search(r"[?&]page=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product-thumb.uni-item"):
        # --- product ID ---
        pid_btn = card.select_one("button[data-pid]")
        product_id = pid_btn.get("data-pid", "") if pid_btn else ""

        # --- title & URL ---
        name_link = card.select_one("a.product-thumb__name")
        title = name_link.get_text(strip=True) if name_link else ""
        url = name_link["href"] if name_link and name_link.get("href") else ""

        # --- description / short specs ---
        desc_el = card.select_one(".product-thumb__description")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # --- pricing ---
        price_div = card.select_one(".product-thumb__price")
        price_azn = None
        old_price_azn = None
        discount_azn = None

        if price_div:
            try:
                original = float(price_div.get("data-price", 0) or 0)
                special = float(price_div.get("data-special", 0) or 0)
                diff = float(price_div.get("data-diff", 0) or 0)
            except (ValueError, TypeError):
                original = special = diff = 0.0

            if special and special > 0:
                price_azn = special
                old_price_azn = original
                discount_azn = abs(diff)
            else:
                price_azn = original

        # --- availability ---
        avail_el = card.select_one(".qty-indicator__text")
        availability = avail_el.get_text(strip=True) if avail_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "description": description,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "availability": availability,
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
