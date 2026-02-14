"""
Scraper for soliton.az laptops (sectionID=66).
Saves all products to data/soliton.csv.
"""

import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://soliton.az"
AJAX_URL = f"{BASE_URL}/ajax-requests.php"
SECTION_ID = "66"
LIMIT = 15
OUTPUT = Path(__file__).parent.parent / "data" / "soliton.csv"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/az/komputer-ve-aksesuarlar/notbuklar/",
    "Origin": BASE_URL,
}

CSV_FIELDS = [
    "product_id",
    "title",
    "brand_id",
    "url",
    "price_azn",
    "credit_price_azn",
    "discount_percent",
    "discount_amount_azn",
    "monthly_6_azn",
    "monthly_12_azn",
    "monthly_18_azn",
    "special_offers",
    "position",
    "data_filters",
]


def fetch_page(offset: int) -> dict:
    payload = urllib.parse.urlencode({
        "action": "loadProducts",
        "sectionID": SECTION_ID,
        "brandID": "0",
        "offset": str(offset),
        "limit": str(LIMIT),
        "sorting": "",
    }).encode()

    req = urllib.request.Request(AJAX_URL, data=payload, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product-item"):
        # --- data attributes ---
        title = card.get("data-title", "").strip()
        price_raw = card.get("data-price", "")
        brand_id = card.get("data-brandid", "")
        position = card.get("data-position", "")
        data_filters = card.get("data-filters", "").strip()

        try:
            price_azn = float(price_raw) if price_raw else None
        except ValueError:
            price_azn = None

        # --- product id & url ---
        compare_span = card.select_one("span.icon.compare")
        product_id = compare_span.get("data-item-id", "") if compare_span else ""

        link = card.select_one("a.prodTitle") or card.select_one("a.thumbHolder")
        url = (BASE_URL + link["href"]) if link and link.get("href") else ""

        # --- credit price ---
        credit_span = card.select_one(".prodPrice .creditPrice")
        credit_price_azn = None
        if credit_span:
            credit_text = credit_span.get_text(strip=True).replace("AZN", "").strip()
            try:
                credit_price_azn = float(credit_text)
            except ValueError:
                pass

        # --- discount ---
        discount_percent = ""
        discount_amount_azn = None
        sale_star = card.select_one(".saleStar")
        if sale_star:
            pct = sale_star.select_one(".percent")
            discount_percent = pct.get_text(strip=True) if pct else ""
            amt = sale_star.select_one(".moneydif .amount")
            if amt:
                try:
                    discount_amount_azn = float(amt.get_text(strip=True).replace("-", "").strip())
                except ValueError:
                    pass

        # --- monthly payments ---
        monthly = {}
        for mp in card.select(".monthlyPayment"):
            month = mp.get("data-month", "")
            amt_span = mp.select_one(".amount")
            if month and amt_span:
                try:
                    monthly[month] = float(amt_span.get_text(strip=True))
                except ValueError:
                    pass

        # --- special offers ---
        offers = [s.get_text(strip=True) for s in card.select(".specialOffers .offer .label")]
        special_offers = " | ".join(offers)

        products.append({
            "product_id": product_id,
            "title": title,
            "brand_id": brand_id,
            "url": url,
            "price_azn": price_azn,
            "credit_price_azn": credit_price_azn,
            "discount_percent": discount_percent,
            "discount_amount_azn": discount_amount_azn,
            "monthly_6_azn": monthly.get("6", ""),
            "monthly_12_azn": monthly.get("12", ""),
            "monthly_18_azn": monthly.get("18", ""),
            "special_offers": special_offers,
            "position": position,
            "data_filters": data_filters,
        })

    return products


def scrape_all() -> list[dict]:
    print(f"Starting scrape — sectionID={SECTION_ID}, limit={LIMIT}")
    all_products: list[dict] = []
    offset = 0

    while True:
        print(f"  Fetching offset={offset} ...", end=" ", flush=True)
        resp = fetch_page(offset)
        total = resp.get("totalCount", "?")
        has_more = resp.get("hasMore", False)

        page_products = parse_products(resp["html"])
        all_products.extend(page_products)
        print(f"got {len(page_products)} products  (total so far: {len(all_products)}/{total})")

        if not has_more:
            break

        offset += LIMIT
        time.sleep(0.5)  # polite delay

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
