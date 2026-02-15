"""
Scraper for notecomp.az laptops.
URL pattern: https://notecomp.az/noutbuklar?page={page}
Last page discovered via '>|' pagination link.
Saves all products to data/notecomp.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://notecomp.az"
CATEGORY_URL = f"{BASE_URL}/noutbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "notecomp.csv"

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
    "discount_percent",
    "is_new",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    """Return last page from the '>|' pagination link."""
    max_page = 1
    for link in soup.select("ul.pagination a"):
        href = link.get("href", "")
        m = re.search(r"[?&]page=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(text: str) -> float | None:
    """Convert '1,033AZN' or '825AZN' -> float."""
    if not text:
        return None
    # Remove AZN, spaces, then strip commas used as thousands separators
    cleaned = text.replace("AZN", "").replace(" ", "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product-thumb"):
        # --- title & URL ---
        name_link = card.select_one(".product-name a")
        title = name_link.get_text(strip=True) if name_link else ""
        url = name_link.get("href", "") if name_link else ""

        # --- product ID from price span class: price_no_format_{id} ---
        product_id = ""
        pid_span = card.select_one("[class*=price_no_format_], [class*=special_no_format_]")
        if pid_span:
            cls_str = " ".join(pid_span.get("class", []))
            m = re.search(r"(?:price_no_format|special_no_format)_(\d+)", cls_str)
            product_id = m.group(1) if m else ""

        # Fallback: extract from wishlist/compare button onclick
        if not product_id:
            btn = card.select_one("button[onclick*=wishlist], button[onclick*=compare]")
            if btn:
                m = re.search(r"'(\d+)'", btn.get("onclick", ""))
                product_id = m.group(1) if m else ""

        # --- prices ---
        old_el = card.select_one(".price-old")
        new_el = card.select_one(".price-new")

        old_price_azn = parse_price(old_el.get_text(strip=True)) if old_el else None
        price_azn = parse_price(new_el.get_text(strip=True)) if new_el else None

        # If no old/new split, parse the single price
        if price_azn is None:
            price_p = card.select_one("p.price")
            if price_p:
                price_azn = parse_price(price_p.get_text(strip=True))

        # --- discount percentage ---
        pct_el = card.select_one(".procent-skidka")
        discount_percent = ""
        if pct_el:
            discount_percent = pct_el.get_text(strip=True)

        # --- is_new badge ---
        new_badge = card.select_one(".sticker-ns.newproduct")
        is_new = bool(new_badge)

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_percent": discount_percent,
            "is_new": is_new,
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
