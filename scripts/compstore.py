"""
Scraper for compstore.az laptops (custom PHP CMS).
URL pattern: https://compstore.az/kateqoriya/noutbuki.html?action=yes&taxonomy_id=91&taxonomy_page=kateqoriya&s={page}
Product data parsed from li.product cards in server-rendered HTML.
Last page discovered from max s= value in ul.pagination links.
Saves all products to data/compstore.csv.
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://compstore.az"
CATEGORY_URL = (
    f"{BASE_URL}/kateqoriya/noutbuki.html"
    "?action=yes&taxonomy_id=91&taxonomy_page=kateqoriya"
)
OUTPUT = Path(__file__).parent.parent / "data" / "compstore.csv"

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
    "monthly_payment_azn",
    "specs",
]


def fetch_page(page: int) -> str:
    url = f"{CATEGORY_URL}&s={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_last_page(soup: BeautifulSoup) -> int:
    max_page = 1
    for a in soup.select("ul.pagination a"):
        href = a.get("href", "")
        m = re.search(r"s=(\d+)", href)
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def parse_monthly(badge_el) -> float | None:
    """Parse '121₼ ayda' -> 121.0"""
    if not badge_el:
        return None
    text = badge_el.get_text(" ", strip=True)
    m = re.search(r"([\d,\.]+)\s*₼", text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("li.product"):
        article = card.select_one("article.product-inner")
        product_id = article.get("data-id", "") if article else ""

        # --- title & URL ---
        title_el = card.select_one("h5 a")
        title = title_el.get_text(strip=True) if title_el else ""
        url = title_el.get("href", "") if title_el else ""
        if url and not url.startswith("http"):
            url = BASE_URL + url

        # --- price ---
        price_el = card.select_one("span.final-price")
        price_azn = None
        if price_el:
            try:
                price_azn = float(price_el.get_text(strip=True).replace(",", ""))
            except ValueError:
                pass

        # --- monthly payment badge ---
        badge_el = card.select_one("div.product-badge")
        monthly_payment_azn = parse_monthly(badge_el)

        # --- specs / excerpt ---
        specs_el = card.select_one("p.product-excerpt a, p.product-excerpt")
        specs = specs_el.get_text(" ", strip=True) if specs_el else ""

        products.append({
            "product_id": product_id,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "monthly_payment_azn": monthly_payment_azn,
            "specs": specs,
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
