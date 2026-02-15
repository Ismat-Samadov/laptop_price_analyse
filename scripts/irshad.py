"""
Scraper for irshad.az laptops.
Uses a session + CSRF token to call the AJAX listing endpoint.
AJAX URL: https://irshad.az/az/list-products/notbuk-planset-ve-komputer-texnikasi/notbuklar
Pagination driven by #loadMore[data-page] — stops when button is absent.
Saves all products to data/irshad.csv.
"""

import csv
import re
import time
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://irshad.az"
MAIN_URL = f"{BASE_URL}/az/notbuk-planset-ve-komputer-texnikasi/notbuklar"
AJAX_URL = f"{BASE_URL}/az/list-products/notbuk-planset-ve-komputer-texnikasi/notbuklar"
OUTPUT = Path(__file__).parent.parent / "data" / "irshad.csv"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36"
)

CSV_FIELDS = [
    "product_code",
    "title",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "availability",
    "labels",
    "monthly_payment_azn",
]


def make_session() -> tuple[urllib.request.OpenerDirector, str]:
    """Return (opener_with_cookies, csrf_token) by loading the main page."""
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    req = urllib.request.Request(
        MAIN_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with opener.open(req, timeout=30) as r:
        html = r.read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    csrf = meta["content"] if meta else ""
    return opener, csrf


def fetch_page(opener: urllib.request.OpenerDirector, csrf: str, page: int) -> str:
    url = f"{AJAX_URL}?q=&price_from=&price_to=&sort=first_pinned&page={page}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-CSRF-TOKEN": csrf,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": MAIN_URL,
        },
    )
    with opener.open(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_price(text: str) -> float | None:
    """Convert '2 429.99 AZN' or '2429.99 AZN' -> 2429.99"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.,]", "", text).replace(",", ".")
    # Remove thousands separators (spaces already stripped above)
    parts = cleaned.split(".")
    if len(parts) > 2:
        # e.g. '2.429.99' -> join all but last with nothing, keep last as decimal
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("div.product"):
        # --- product code ---
        # Use the first basket button's data-code (selected / primary variant)
        basket_btn = card.select_one("a.basket_button[data-code]")
        product_code = basket_btn.get("data-code", "") if basket_btn else ""

        # Fallback: extract numeric ID from card class  product-{id}_uuid
        if not product_code:
            m = re.search(r"product-(\d+)_", " ".join(card.get("class", [])))
            product_code = m.group(1) if m else ""

        # --- name & URL ---
        name_link = card.select_one("a.product__name")
        title = name_link.get_text(strip=True) if name_link else ""
        url = name_link.get("href", "") if name_link else ""

        # --- prices (first block = selected variant) ---
        price_block = card.select_one(".product__price__current")
        old_price_azn = None
        price_azn = None
        discount_azn = None

        if price_block:
            old_el = price_block.select_one(".old-price")
            new_el = price_block.select_one(".new-price")
            if old_el:
                old_price_azn = parse_price(old_el.get_text(strip=True))
            if new_el:
                price_azn = parse_price(new_el.get_text(strip=True))
            # If no old price, the displayed price is in new-price without discount
            if price_azn and old_price_azn and old_price_azn > price_azn:
                discount_azn = round(old_price_azn - price_azn, 2)
            elif price_azn and not old_price_azn:
                # no discount, parse from any single price text
                pass

        # Fallback: parse price from label if price_block missing
        if price_azn is None:
            single = card.select_one(".product__price")
            if single:
                price_azn = parse_price(single.get_text(strip=True))

        # --- labels (availability + discount) ---
        labels_div = card.select_one(".product__labels")
        labels = ""
        availability = ""
        if labels_div:
            labels = labels_div.get_text(" ", strip=True)
            avail_el = labels_div.select_one(".product__label--light-purple")
            availability = avail_el.get_text(strip=True) if avail_el else ""

        # --- monthly installment (first ppl-price block) ---
        ppl_price = card.select_one(".ppl-price")
        monthly_payment_azn = None
        if ppl_price:
            monthly_payment_azn = parse_price(ppl_price.get_text(strip=True))

        # discount label from orange label e.g. "-310 AZN"
        if discount_azn is None:
            disc_el = labels_div.select_one(".product__label--orange") if labels_div else None
            if disc_el:
                disc_text = disc_el.get_text(strip=True)
                m = re.search(r"[\d.,]+", disc_text)
                if m:
                    try:
                        discount_azn = float(m.group().replace(",", "."))
                    except ValueError:
                        pass

        products.append({
            "product_code": product_code,
            "title": title,
            "url": url,
            "price_azn": price_azn,
            "old_price_azn": old_price_azn,
            "discount_azn": discount_azn,
            "availability": availability,
            "labels": labels,
            "monthly_payment_azn": monthly_payment_azn,
        })

    return products


def scrape_all() -> list[dict]:
    print(f"Starting scrape — {AJAX_URL}")
    print("  Initialising session (fetching CSRF token) ...", end=" ", flush=True)
    opener, csrf = make_session()
    print("done")

    all_products: list[dict] = []
    page = 1

    while True:
        print(f"  Fetching page {page} ...", end=" ", flush=True)
        html = fetch_page(opener, csrf, page)
        soup = BeautifulSoup(html, "html.parser")

        page_products = parse_products(html)
        all_products.extend(page_products)

        # Check for next page
        load_more = soup.select_one("#loadMore")
        next_page = load_more.get("data-page") if load_more else None

        print(f"got {len(page_products)} products  (total: {len(all_products)})  next={next_page}")

        if not next_page:
            break

        page = int(next_page)
        time.sleep(0.6)

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
