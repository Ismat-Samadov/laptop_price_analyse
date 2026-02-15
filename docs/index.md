# Documentation Index — Azerbaijan Laptop Price Analysis

This project collects, normalises, and analyses laptop prices from 16 Azerbaijani
e-commerce retailers. The pipeline runs entirely in Python using only the standard
library plus `requests`-free scraping (`urllib`) and `BeautifulSoup`.

---

## Documents

| File | Contents |
|---|---|
| [getting_started.md](getting_started.md) | Installation, dependencies, quickstart |
| [scrapers.md](scrapers.md) | Per-site scraper reference — URLs, pagination, fields, quirks |
| [data_schema.md](data_schema.md) | All CSV column definitions (per-source and unified) |
| [pipeline.md](pipeline.md) | End-to-end pipeline: collect → combine → analyse |
| [charts.md](charts.md) | Chart inventory, methodology, reproduction steps |

---

## Project Layout

```
laptop_price_analyse/
├── data/
│   ├── <site>.csv          # One raw CSV per scraped retailer
│   └── data.csv            # Unified combined dataset (all retailers)
├── scripts/
│   ├── soliton.py          # Scraper — soliton.az
│   ├── kontakt.py          # Scraper — kontakt.az
│   ├── aztechshop.py       # Scraper — aztechshop.az
│   ├── irshad.py           # Scraper — irshad.az
│   ├── notecomp.py         # Scraper — notecomp.az
│   ├── mgstore.py          # Scraper — mgstore.az
│   ├── bakuelectronics.py  # Scraper — bakuelectronics.az
│   ├── techbar.py          # Scraper — techbar.az
│   ├── birmarket.py        # Scraper — birmarket.az
│   ├── compstore.py        # Scraper — compstore.az
│   ├── ctrl.py             # Scraper — ctrl.az
│   ├── brothers.py         # Scraper — brothers.az
│   ├── qiymeti.py          # Scraper — qiymeti.net
│   ├── icomp.py            # Scraper — icomp.az
│   ├── mimelon.py          # Scraper — mimelon.com
│   ├── bytelecom.py        # Scraper — bytelecom.az
│   ├── combine.py          # Merges all per-site CSVs → data/data.csv
│   └── generate_charts.py  # Reads data/data.csv → charts/*.png
├── charts/
│   └── *.png               # 10 business intelligence charts
├── docs/
│   └── *.md                # This documentation
├── prompts/
│   └── analyse.txt         # Original analysis brief
└── README.md               # Executive business report
```

---

## Data Snapshot (February 2026)

| Metric | Value |
|---|---|
| Retailers covered | 16 |
| Total listings | 8,548 |
| Listings with valid price | 7,933 |
| Listings with discount data | 1,838 (23%) |
| Price range | 45 – 13,300 AZN |
| Largest single source | notecomp.az (1,796) |
