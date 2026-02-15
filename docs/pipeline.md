# Pipeline Reference

This document describes the complete data pipeline from raw HTML to finished
charts: what each stage does, what it produces, and how the stages connect.

---

## Overview

```
16 websites
     │
     ▼
┌─────────────────────────────────────────┐
│  Stage 1 — Scrape                       │
│  scripts/<site>.py  →  data/<site>.csv  │
│  (one script per retailer)              │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Stage 2 — Combine                      │
│  scripts/combine.py  →  data/data.csv   │
│  (merges + normalises all per-site CSVs)│
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Stage 3 — Analyse                      │
│  scripts/generate_charts.py             │
│  →  charts/*.png  (10 charts)           │
└─────────────────────────────────────────┘
```

---

## Stage 1 — Scraping

### What happens

Each `scripts/<site>.py` script:
1. Determines the last page (from pagination links or response metadata).
2. Iterates over pages with a polite 0.5–0.6 s delay between requests.
3. Parses every product card on each page with BeautifulSoup.
4. Writes a site-specific CSV to `data/<site>.csv`.

### Inputs / outputs

| Script | Input | Output |
|---|---|---|
| `soliton.py` | POST AJAX (offset pagination) | `data/soliton.csv` |
| `kontakt.py` | GET `?p=` pagination | `data/kontakt.csv` |
| `aztechshop.py` | GET `?page=` pagination | `data/aztechshop.csv` |
| `irshad.py` | GET AJAX + CSRF session | `data/irshad.csv` |
| `notecomp.py` | GET `?page=` pagination | `data/notecomp.csv` |
| `mgstore.py` | GET `?p=` pagination | `data/mgstore.csv` |
| `bakuelectronics.py` | GET `?page=` + `__NEXT_DATA__` JSON | `data/bakuelectronics.csv` |
| `techbar.py` | GET `/page/{n}/` pagination | `data/techbar.csv` |
| `birmarket.py` | GET `?page=` + cookie | `data/birmarket.csv` |
| `compstore.py` | GET `?s=` pagination | `data/compstore.csv` |
| `ctrl.py` | POST Porto AJAX | `data/ctrl.csv` |
| `brothers.py` | GET single large page | `data/brothers.csv` |
| `qiymeti.py` | GET WP admin-ajax | `data/qiymeti.csv` |
| `icomp.py` | GET `?s=` pagination | `data/icomp.csv` |
| `mimelon.py` | GET `/{page}` pagination | `data/mimelon.csv` |
| `bytelecom.py` | GET `?page=` Livewire SSR | `data/bytelecom.csv` |

### Approximate run times

| Site | Pages | ~Time |
|---|---|---|
| notecomp.az | 90 | ~55 s |
| compstore.az | 89 | ~55 s |
| birmarket.az | 31 | ~20 s |
| brothers.az | 1 (single 10 MB page) | ~8 s |
| irshad.az | 46 | ~30 s |
| all others | 1–19 | 1–15 s each |

Total estimated time: **~10–15 minutes** for a complete fresh run.

---

## Stage 2 — Combining

### What `scripts/combine.py` does

1. Reads all 16 per-site CSVs from `data/`.
2. Maps each row to the **unified schema** (15 columns) using site-specific
   field mappings (see [data_schema.md](data_schema.md)).
3. Adds a `source` column with the retailer domain.
4. Writes `data/data.csv`.

### Key field mappings

| Raw column | Source | Unified column |
|---|---|---|
| `discounted_price_azn` | bakuelectronics | `price_azn` |
| `price_azn` | bakuelectronics | `old_price_azn` (if discounted) |
| `product_code` | irshad | `product_id` |
| `description` | aztechshop | `specs` |
| `discount_amount_azn` | soliton | `discount_azn` |
| `monthly_12_azn` | soliton | `monthly_payment_azn` |
| `labels` | irshad, techbar | `label` |
| `badges` | bytelecom | `label` |
| `is_new` | notecomp | `label` → `"new"` |

### Output

`data/data.csv` — **8,548 rows × 15 columns** (February 2026 snapshot).

---

## Stage 3 — Analysis & Charts

### What `scripts/generate_charts.py` does

1. Loads `data/data.csv`.
2. Filters to rows where `price_azn` is a valid positive float (7,933 rows).
3. Runs 10 chart functions, each writing a PNG to `charts/`.

### Chart functions

| Function | Output file |
|---|---|
| `chart_catalog_size()` | `01_catalog_size.png` |
| `chart_price_positioning()` | `02_price_positioning.png` |
| `chart_price_distribution()` | `03_price_distribution.png` |
| `chart_brand_share()` | `04_brand_share.png` |
| `chart_brand_price()` | `05_brand_price.png` |
| `chart_brand_segments()` | `06_brand_segments.png` |
| `chart_discounts()` | `07_discount_strategy.png` |
| `chart_price_spread()` | `08_price_spread.png` |
| `chart_retailer_brand_mix()` | `09_retailer_brand_mix.png` |
| `chart_price_heatmap()` | `10_price_heatmap.png` |

### Brand detection

Brands are inferred from the product title since most sites do not expose a
structured brand field. The detection function checks for these brand strings
(case-insensitive) in the title, stopping at the first match:
`ASUS`, `HP`, `Lenovo`, `Acer`, `MSI`, `Dell`, `Apple`.
Products not matching any of these are classified as `"Other"`.

---

## Data Freshness & Re-running

The data reflects a **point-in-time snapshot** scraped in February 2026.
Prices, listings, and discounts change daily on all platforms.

To refresh the dataset:

```bash
# Re-scrape all sites
for s in scripts/soliton.py scripts/kontakt.py scripts/aztechshop.py \
         scripts/irshad.py scripts/notecomp.py scripts/mgstore.py \
         scripts/bakuelectronics.py scripts/techbar.py scripts/birmarket.py \
         scripts/compstore.py scripts/ctrl.py scripts/brothers.py \
         scripts/qiymeti.py scripts/icomp.py scripts/mimelon.py \
         scripts/bytelecom.py; do
    python3 "$s"
done

# Rebuild unified dataset
python3 scripts/combine.py

# Regenerate charts
python3 scripts/generate_charts.py
```

### Things that can break between runs

| Risk | Affected scraper | Mitigation |
|---|---|---|
| Site redesign changes CSS selectors | All HTML-based scrapers | Re-inspect and update selectors in `parse_products()` |
| Next.js data shape change | `bakuelectronics.py` | Update the key path in `data["props"][...]` |
| CSRF token mechanism change | `irshad.py` | Update `make_session()` — look for new token location |
| birmarket.az cookie expiry | `birmarket.py` | Obtain fresh cookie from browser DevTools |
| Pagination URL change | Any scraper | Update `CATEGORY_URL` and `get_last_page()` |
| New retailer to add | — | Follow the scraper template pattern; add to `SOURCES` dict in `combine.py` |

---

## Adding a New Retailer

1. Create `scripts/<sitename>.py` following the template:
   - `fetch_page(page)` → returns raw HTML string
   - `get_last_page(soup)` → returns int
   - `parse_products(html)` → returns `list[dict]`
   - `scrape_all()` → calls the above, prints progress
   - `save_csv(products, path)` → writes the CSV

2. Identify which unified columns the new site supports and note any
   field-name differences.

3. Add an entry to the `SOURCES` dict in `scripts/combine.py`:
   ```python
   SOURCES = {
       ...
       "sitename": "sitename.az",
   }
   ```

4. Update the `normalize()` function in `combine.py` if the new site has
   non-standard field names.

5. Re-run `combine.py` and `generate_charts.py`.
