"""
Scraper for bytelecom.az laptops (Laravel + Livewire).
URL pattern: https://bytelecom.az/az/category/noutbuklar?page={page}
Page is a standard GET query param — Livewire SSR renders full HTML.
Last page discovered from max gotoPage(N) value in ul.pagination wire buttons.
Prices: h6.discount-price = original, h5.price = current (₼ 2,699.00 format).
Product ID extracted from wire:click="toggleWishlist({id})" button.
Saves all products to data/bytelecom.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://bytelecom.az"
CATEGORY_URL = f"{BASE_URL}/az/category/noutbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "bytelecom.csv"

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
    "badges",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    pag = soup.select_one("ul.pagination")
    if pag:
        for btn in pag.select("button[wire\\:click]"):
            m = re.search(r"gotoPage\((\d+)", btn.get("wire:click", ""))
            if m:
                max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(text: str) -> float | None:
    """Convert '₼ 2,699.00' or '₼ 2,159.00' -> float.
    Comma is thousands separator; dot is decimal separator.
    """
    if not text:
        return None
    cleaned = (
        text.replace("₼", "")
            .replace("\xa0", "")
            .replace(",", "")   # remove thousands comma
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

    for card in soup.select("div.product"):
        # --- product ID from toggleWishlist button ---
        wish_btn = card.select_one("button.favourite-product[wire\\:click]")
        product_id = ""
        if wish_btn:
            m = re.search(r"toggleWishlist\((\d+)\)", wish_btn.get("wire:click", ""))
            if m:
                product_id = m.group(1)

        # --- title & URL ---
        name_el = card.select_one("a.product-name")
        title = name_el.get_text(strip=True) if name_el else ""
        url = name_el.get("href", "") if name_el else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # --- prices ---
        old_el = card.select_one("h6.discount-price")   # original (struck-through)
        cur_el = card.select_one("h5.price")             # current selling price

        old_price_azn = parse_price(old_el.get_text(strip=True)) if old_el else None
        price_azn = parse_price(cur_el.get_text(strip=True)) if cur_el else None

        # If no discount, h6 is absent — only h5 present
        if price_azn is None and old_price_azn is not None:
            price_azn, old_price_azn = old_price_azn, None

        discount_azn = None
        if old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # --- badges ---
        badge_els = card.select("div.badge-item p")
        badges = " | ".join(b.get_text(strip=True) for b in badge_els if b.get_text(strip=True))

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "badges": badges,
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
