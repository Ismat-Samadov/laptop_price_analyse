"""
Scraper for ctrl.az laptops (WordPress / Porto WooCommerce theme).
URL pattern: POST https://ctrl.az/product-tag/notebooklar/page/{page}/
Payload: portoajax=true&load_posts_only=true
Returns partial HTML fragment with product cards.
Last page discovered from ul.page-numbers links.
Saves all products to data/ctrl.csv.
"""

import csv
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://ctrl.az"
TAG_URL = f"{BASE_URL}/product-tag/notebooklar"
OUTPUT = Path(__file__).parent.parent / "data" / "ctrl.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
    "Referer": f"{TAG_URL}/",
    "DNT": "1",
}

PAYLOAD = urllib.parse.urlencode({
    "portoajax": "true",
    "load_posts_only": "true",
}).encode()

CSV_FIELDS = [
    "product_id",
    "title",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "discount_percent",
]


def fetch_page(page: int) -> str:
    url = f"{TAG_URL}/" if page == 1 else f"{TAG_URL}/page/{page}/"
    req = urllib.request.Request(url, data=PAYLOAD, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for a in soup.select("ul.page-numbers a"):
        href = a.get("href", "")
        m = re.search(r"/page/(\d+)/", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_price(bdi_el) -> float | None:
    """Parse '900,00₼' or '779,00 ₼' -> float (comma is decimal separator)."""
    if not bdi_el:
        return None
    text = bdi_el.get_text(strip=True)
    text = text.replace("₼", "").replace("\xa0", "").replace(" ", "").strip()
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("li.product"):
        # --- product ID from li class list: post-{id} ---
        classes = " ".join(card.get("class", []))
        pid_m = re.search(r"\bpost-(\d+)\b", classes)
        product_id = pid_m.group(1) if pid_m else ""

        # --- title & URL ---
        title_el = card.select_one("h3.woocommerce-loop-product__title")
        title = title_el.get_text(strip=True) if title_el else ""

        link = card.select_one("a.product-loop-title")
        url = link.get("href", "") if link else ""

        # --- prices (WooCommerce del/ins pattern) ---
        del_el = card.select_one("del .woocommerce-Price-amount bdi")
        ins_el = card.select_one("ins .woocommerce-Price-amount bdi")

        old_price_azn = parse_price(del_el)
        price_azn = parse_price(ins_el)

        # No sale — single price
        if price_azn is None:
            single = card.select_one(".woocommerce-Price-amount bdi")
            price_azn = parse_price(single)

        discount_azn = None
        if old_price_azn and price_azn and old_price_azn > price_azn:
            discount_azn = round(old_price_azn - price_azn, 2)

        # --- discount label ---
        sale_el = card.select_one(".labels .onsale")
        discount_percent = sale_el.get_text(strip=True) if sale_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "discount_percent": discount_percent,
        })

    return products


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {TAG_URL}")

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
