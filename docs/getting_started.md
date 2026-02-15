# Getting Started

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or later (uses `float \| None` union syntax) |
| beautifulsoup4 | ≥ 4.12 |
| matplotlib | ≥ 3.8 |
| numpy | ≥ 1.26 |

All HTTP requests are made with the Python standard library (`urllib.request`).
No `requests`, `selenium`, or `playwright` is required.

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd laptop_price_analyse

# 2. Install Python dependencies
pip install beautifulsoup4 matplotlib numpy
```

---

## Running a Single Scraper

Each script in `scripts/` is self-contained and can be run individually:

```bash
python3 scripts/kontakt.py
# → writes data/kontakt.csv

python3 scripts/birmarket.py
# → writes data/birmarket.csv
```

Progress is printed to stdout:

```
Starting scrape — https://kontakt.az/notbuk-ve-kompyuterler/komputerler/notbuklar
  Fetching page 1 (discovering pagination) ... last page = 13
  Page 1: 20 products  (total: 20)
  Fetching page 2/13 ... got 20 products  (total: 40)
  ...
Saved 258 rows -> data/kontakt.csv
```

---

## Running All Scrapers

```bash
for script in scripts/soliton.py scripts/kontakt.py scripts/aztechshop.py \
              scripts/irshad.py scripts/notecomp.py scripts/mgstore.py \
              scripts/bakuelectronics.py scripts/techbar.py scripts/birmarket.py \
              scripts/compstore.py scripts/ctrl.py scripts/brothers.py \
              scripts/qiymeti.py scripts/icomp.py scripts/mimelon.py \
              scripts/bytelecom.py; do
    echo "=== $script ==="
    python3 "$script"
done
```

Expected total run time: approximately 10–15 minutes (polite 0.5 s delay between requests per scraper).

---

## Combining into the Master Dataset

After all per-site CSVs exist in `data/`:

```bash
python3 scripts/combine.py
# → writes data/data.csv  (8,548 rows, 15 columns + source)
```

---

## Generating Charts

```bash
python3 scripts/generate_charts.py
# → writes 10 PNG files to charts/
```

Requires `data/data.csv` to exist first. Charts are saved at 150 DPI.

---

## Full Pipeline (one command sequence)

```bash
# Step 1 – scrape all sites
for s in scripts/soliton.py scripts/kontakt.py scripts/aztechshop.py \
         scripts/irshad.py scripts/notecomp.py scripts/mgstore.py \
         scripts/bakuelectronics.py scripts/techbar.py scripts/birmarket.py \
         scripts/compstore.py scripts/ctrl.py scripts/brothers.py \
         scripts/qiymeti.py scripts/icomp.py scripts/mimelon.py \
         scripts/bytelecom.py; do python3 "$s"; done

# Step 2 – combine
python3 scripts/combine.py

# Step 3 – charts
python3 scripts/generate_charts.py
```

---

## Notes on Network Behaviour

- All scrapers include a `time.sleep(0.5)` or `time.sleep(0.6)` delay between page requests to avoid overloading servers.
- Timeouts are set to 30 seconds per request (60 seconds for brothers.az which returns a ~10 MB page).
- No authentication is required for any scraper except `birmarket.az`, which requires a `Cookie` header (`auth.strategy=local; cityId=1; citySelected=true`) to receive city-specific prices. This cookie is hardcoded; it does not expire.
- `irshad.az` performs a two-step session initialisation: it first fetches the main page to capture a CSRF token and session cookie, then uses those for all AJAX requests. This is handled automatically inside `irshad.py`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: bs4` | BeautifulSoup not installed | `pip install beautifulsoup4` |
| `urllib.error.HTTPError: 403` | Site added bot protection | Retry after a few minutes; adjust `User-Agent` if persistent |
| `urllib.error.URLError: timed out` | Slow connection or site overloaded | Increase `timeout=` in `urllib.request.urlopen()` |
| 0 products parsed | Site changed its HTML structure | Inspect the live page and update the CSS selector in `parse_products()` |
| `SyntaxError` on Python 3.9 | `float \| None` union syntax requires 3.10+ | Upgrade Python or replace with `Optional[float]` |
