"""
Combines all individual site CSVs into data/data.csv.
Adds a 'source' column identifying the originating website.
Maps site-specific column names to a unified schema.

Unified columns:
  source, product_id, title, url, price_azn, old_price_azn,
  discount_azn, discount_percent, brand, specs, availability,
  label, monthly_payment_azn, rating, review_count
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT = DATA_DIR / "data.csv"

UNIFIED_FIELDS = [
    "source",
    "product_id",
    "title",
    "url",
    "price_azn",
    "old_price_azn",
    "discount_azn",
    "discount_percent",
    "brand",
    "specs",
    "availability",
    "label",
    "monthly_payment_azn",
    "rating",
    "review_count",
]


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def normalize(row: dict, source: str) -> dict:
    """Map a site-specific row dict to the unified schema."""
    out = {f: "" for f in UNIFIED_FIELDS}
    out["source"] = source

    # --- product_id ---
    # irshad uses 'product_code'; bakuelectronics also has 'product_code' alongside 'product_id'
    out["product_id"] = (
        row.get("product_id")
        or row.get("product_code")
        or ""
    )

    # --- core fields ---
    out["title"] = row.get("title", "")
    out["url"]   = row.get("url", "")

    # --- price_azn (current selling price) ---
    # bakuelectronics: selling price is 'discounted_price_azn'
    out["price_azn"] = (
        row.get("discounted_price_azn")     # bakuelectronics
        or row.get("price_azn")
        or ""
    )

    # --- old_price_azn (original before discount) ---
    # bakuelectronics: original price is 'price_azn' (if discounted)
    if source == "bakuelectronics":
        disc = row.get("discount_azn", "")
        out["old_price_azn"] = row.get("price_azn", "") if disc else ""
    else:
        out["old_price_azn"] = row.get("old_price_azn", "")

    # --- discount ---
    out["discount_azn"]     = row.get("discount_azn", "") or row.get("discount_amount_azn", "")
    out["discount_percent"] = row.get("discount_percent", "")

    # --- brand ---
    out["brand"] = row.get("brand", "") or row.get("brand_id", "")

    # --- specs (also covers 'description' from aztechshop) ---
    out["specs"] = row.get("specs", "") or row.get("description", "")

    # --- availability ---
    out["availability"] = row.get("availability", "")

    # --- label (covers label / labels / badges / is_new) ---
    label_parts = []
    for key in ("label", "labels", "badges"):
        val = row.get(key, "").strip()
        if val:
            label_parts.append(val)
    if row.get("is_new", "").strip():
        label_parts.append("new")
    out["label"] = " | ".join(label_parts)

    # --- monthly_payment_azn ---
    # soliton uses monthly_6_azn / monthly_12_azn / monthly_18_azn; use 12-month as proxy
    out["monthly_payment_azn"] = (
        row.get("monthly_payment_azn")
        or row.get("monthly_12_azn")
        or row.get("credit_price_azn")
        or ""
    )

    # --- rating / review_count (bakuelectronics only) ---
    out["rating"]       = row.get("rating", "")
    out["review_count"] = row.get("review_count", "")

    return out


# Map: CSV filename stem -> source label
SOURCES = {
    "soliton":          "soliton.az",
    "kontakt":          "kontakt.az",
    "aztechshop":       "aztechshop.az",
    "irshad":           "irshad.az",
    "notecomp":         "notecomp.az",
    "mgstore":          "mgstore.az",
    "bakuelectronics":  "bakuelectronics.az",
    "techbar":          "techbar.az",
    "birmarket":        "birmarket.az",
    "compstore":        "compstore.az",
    "ctrl":             "ctrl.az",
    "brothers":         "brothers.az",
    "qiymeti":          "qiymeti.net",
    "icomp":            "icomp.az",
    "mimelon":          "mimelon.com",
    "bytelecom":        "bytelecom.az",
}


def main() -> None:
    all_rows: list[dict] = []

    for stem, source in SOURCES.items():
        path = DATA_DIR / f"{stem}.csv"
        if not path.exists():
            print(f"  [SKIP] {path.name} not found")
            continue
        rows = read_csv(path)
        normalized = [normalize(r, source) for r in rows]
        all_rows.extend(normalized)
        print(f"  {source:30s} {len(rows):>5} rows")

    print(f"\nTotal: {len(all_rows)} rows")

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=UNIFIED_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved -> {OUTPUT}")


if __name__ == "__main__":
    main()
