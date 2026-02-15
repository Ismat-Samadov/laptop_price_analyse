# Charts Reference

This document describes every chart produced by `scripts/generate_charts.py`:
what question it answers, which columns it uses, how the calculation works,
and how to reproduce or extend it.

---

## Overview

| # | File | Chart type | Primary question |
|---|---|---|---|
| 1 | `01_catalog_size.png` | Horizontal bar | Who controls the most shelf space? |
| 2 | `02_price_positioning.png` | Grouped bar | In which price tier does each retailer compete? |
| 3 | `03_price_distribution.png` | Vertical bar | Where does market demand live by price bracket? |
| 4 | `04_brand_share.png` | Horizontal bar | Which brands dominate by listing volume? |
| 5 | `05_brand_price.png` | Grouped bar | Which brands are premium vs. volume? |
| 6 | `06_brand_segments.png` | 100% stacked bar | Where does each brand play across price tiers? |
| 7 | `07_discount_strategy.png` | Dual-axis grouped bar | How aggressively does each retailer discount? |
| 8 | `08_price_spread.png` | Range bar (overlay) | How wide is the price gap for identical models? |
| 9 | `09_retailer_brand_mix.png` | 100% stacked bar | Which brands does each retailer specialise in? |
| 10 | `10_price_heatmap.png` | Colour heatmap | What does each retailer charge per brand on average? |

All charts are saved at **150 DPI** to `charts/` with a `#FAFAFA` background.

---

## Shared Methodology

### Input filter

`generate_charts.py` filters `data/data.csv` to rows where `price_azn` is a
valid positive float before running any chart function. This removes:

- Rows where `price_azn` is blank (retailer did not expose a price).
- Rows where the price could not be parsed as a number.

The filtered set is called `priced` throughout the script. The February 2026
snapshot contains **8,548 total rows → 7,933 priced rows**.

### Brand detection

Because most retailers do not expose a structured brand field, brands are
inferred from the product title using case-insensitive substring matching.
The detection function checks these strings in order, stopping at the first
match:

```
ASUS → HP → Lenovo → Acer → MSI → Dell → Apple
```

Products matching none of the above are classified as `"Other"`. The order
matters: a title containing both `ASUS` and `HP` (rare) would be classified
as `ASUS`.

Source: `detect_brand()` at `scripts/generate_charts.py:70`.

---

## Chart 1 — Catalog Size by Retailer

**Output:** `charts/01_catalog_size.png`
**Function:** `chart_catalog_size()` — `scripts/generate_charts.py:87`

### What it shows

A horizontal bar chart of how many priced listings each retailer contributes
to the dataset, sorted from fewest to most.

### Columns used

| Column | Role |
|---|---|
| `source` | Groups rows by retailer |
| `price_azn` | Only rows with a valid price are counted |

### Calculation

```python
src_count = Counter(src for src, _, _ in priced)
```

Each row in `priced` contributes +1 to its source's count. Bars are sorted
ascending so the largest retailer appears at the top of the horizontal chart.

### Interpretation notes

- Listing count reflects what the scraper found on the laptop/notebook
  category page of each site on the scrape date.
- A high count does not imply higher revenue — it reflects catalog breadth.
- Retailers with counts under 100 may be niche or have poor category coverage.

---

## Chart 2 — Price Positioning by Retailer

**Output:** `charts/02_price_positioning.png`
**Function:** `chart_price_positioning()` — `scripts/generate_charts.py:106`

### What it shows

A grouped bar chart with two bars per retailer: **average price** (blue) and
**median price** (green). Retailers are sorted by average price ascending.

### Columns used

| Column | Role |
|---|---|
| `source` | Groups rows by retailer |
| `price_azn` | The selling price used for average / median |

### Calculation

```python
src_prices = defaultdict(list)
for src, p, _ in priced:
    src_prices[src].append(p)

data = [(src, statistics.mean(ps), statistics.median(ps))
        for src, ps in src_prices.items()]
```

`statistics.mean` and `statistics.median` from the Python standard library
are used — no external dependency.

### Interpretation notes

- A large gap between average and median indicates skew — a small number of
  very expensive (or cheap) products is pulling the mean away from the
  typical product.
- A retailer with a high average but moderate median is likely carrying a
  few flagship/gaming models that inflate the mean.

---

## Chart 3 — Market Price Distribution

**Output:** `charts/03_price_distribution.png`
**Function:** `chart_price_distribution()` — `scripts/generate_charts.py:139`

### What it shows

A vertical bar chart showing how all 7,933 priced listings distribute across
six price brackets. Each bar is labelled with its percentage of total.

### Columns used

| Column | Role |
|---|---|
| `price_azn` | Assigned to bracket |

### Price brackets

| Bracket label | Range |
|---|---|
| Under 500 | `price_azn < 500` |
| 500–999 | `500 ≤ price_azn < 1,000` |
| 1,000–1,999 | `1,000 ≤ price_azn < 2,000` |
| 2,000–2,999 | `2,000 ≤ price_azn < 3,000` |
| 3,000–4,999 | `3,000 ≤ price_azn < 5,000` |
| 5,000+ | `price_azn ≥ 5,000` |

### Calculation

Each row is iterated once; the first bracket whose upper limit exceeds the
price receives the count increment.

### Interpretation notes

- This chart intentionally uses absolute counts (not percentages) on the
  y-axis, with the percentage annotated above each bar, to show both volume
  and proportion simultaneously.
- The 1,000–1,999 AZN bracket dominates the market — roughly 43% of
  listings.

---

## Chart 4 — Brand Market Share by Listing Volume

**Output:** `charts/04_brand_share.png`
**Function:** `chart_brand_share()` — `scripts/generate_charts.py:169`

### What it shows

A horizontal bar chart of total listing counts for the seven tracked brands,
sorted from fewest to most. The `"Other"` bucket is excluded to keep the
chart focused on named brands.

### Columns used

| Column | Role |
|---|---|
| `title` | Brand detected via `detect_brand()` |
| `price_azn` | Only priced rows are included |

### Calculation

```python
brand_count = Counter(detect_brand(r["title"]) for _, _, r in priced)
data = [(b, brand_count[b]) for b in BRANDS if brand_count[b] > 0]
```

### Interpretation notes

- "Market share" here means share of **listings**, not revenue.
- A brand with 2,000 listings may still be outsold in revenue by a brand
  with 200 listings if the latter's products have 10× the price.

---

## Chart 5 — Average Price by Brand

**Output:** `charts/05_brand_price.png`
**Function:** `chart_brand_price()` — `scripts/generate_charts.py:191`

### What it shows

A grouped bar chart of average and median selling price per brand, for the
seven tracked brands only (excludes `"Other"`). Sorted by average ascending.

### Columns used

| Column | Role |
|---|---|
| `title` | Brand detected via `detect_brand()` |
| `price_azn` | Grouped into per-brand price lists |

### Calculation

Same logic as Chart 2 but grouped by brand instead of retailer:

```python
brand_prices = defaultdict(list)
for _, p, r in priced:
    b = detect_brand(r["title"])
    if b != "Other":
        brand_prices[b].append(p)
```

### Interpretation notes

- A brand's average price reflects its **product mix** in the Azerbaijani
  market, not necessarily its global positioning. A brand with few SKUs
  concentrated in the premium tier will show a high average even if it also
  sells budget models internationally.

---

## Chart 6 — Price Segment Mix per Brand

**Output:** `charts/06_brand_segments.png`
**Function:** `chart_brand_segments()` — `scripts/generate_charts.py:225`

### What it shows

A 100% stacked bar chart: for each of the seven brands, the percentage of its
listings falling into four price tiers. Brands are sorted by total listing
count ascending (left = fewest).

### Columns used

| Column | Role |
|---|---|
| `title` | Brand detected via `detect_brand()` |
| `price_azn` | Assigned to one of four tiers |

### Price tiers

| Tier label | Range | Bar colour |
|---|---|---|
| Under 1,000 | `price_azn < 1,000` | Green |
| 1,000–1,999 | `1,000 ≤ price_azn < 2,000` | Blue |
| 2,000–2,999 | `2,000 ≤ price_azn < 3,000` | Amber |
| 3,000+ | `price_azn ≥ 3,000` | Red |

### Calculation

Counts per brand per tier are normalised to percentages before plotting:

```python
seg_pcts[seg_i] = [brand_segs[b][seg_i] / sum(brand_segs[b]) * 100 for b in brands_ord]
```

Segment labels are displayed inside bars only when the segment exceeds 8%
of the bar height, to avoid overprinting.

---

## Chart 7 — Discount Strategy by Retailer

**Output:** `charts/07_discount_strategy.png`
**Function:** `chart_discounts()` — `scripts/generate_charts.py:277`

### What it shows

A dual-axis grouped bar chart. Left axis (blue): percentage of each
retailer's listings that carry a discount. Right axis (red): average discount
depth as a percentage.

**Only retailers that publish both `discount_azn` and `old_price_azn` appear
on this chart.** Retailers that do not expose original prices are excluded.

### Columns used

| Column | Role |
|---|---|
| `source` | Groups by retailer |
| `discount_azn` | Numerator for depth calculation |
| `old_price_azn` | Denominator for depth calculation |
| `price_azn` | Total listing count denominator (from `priced`) |

### Calculation

A row is counted as discounted if both `discount_azn > 0` and
`old_price_azn > 0` are parseable floats.

Discount depth is computed as:

```
depth % = discount_azn / old_price_azn × 100
```

Frequency is:

```
freq % = number_of_discounted_rows / total_rows_for_source × 100
```

### Interpretation notes

- Retailers not shown (notecomp.az, compstore.az, brothers.az, qiymeti.net,
  soliton.az, bakuelectronics.az) do not expose original prices in their
  listing data, so discount frequency and depth cannot be measured.
- `discount_azn` is either scraped directly from a data attribute or
  computed as `old_price_azn − price_azn` in the individual scrapers.

---

## Chart 8 — Price Spread on Identical Models Across Retailers

**Output:** `charts/08_price_spread.png`
**Function:** `chart_price_spread()` — `scripts/generate_charts.py:321`

### What it shows

For products listed on **three or more retailers**, the range between the
cheapest and most expensive price found. Shows the top 12 products by
percentage spread. Green bar = lowest price found; red bar = highest price.

### Columns used

| Column | Role |
|---|---|
| `title` | Product identity (normalised) |
| `source` | Retailer identity |
| `price_azn` | Price to compare |

### Calculation

1. Product titles are lowercased and collapsed whitespace (`clean()`).
2. Rows are grouped by `(cleaned_title, source)`.
3. Only titles that appear on **3 or more distinct sources** are considered.
4. For each qualifying title, the minimum price per source is taken (to avoid
   counting duplicate listings on the same retailer).
5. Spread % = `(max_price − min_price) / min_price × 100`.
6. Top 12 by spread % are plotted.

```python
if len(src_prices_d) < 3:
    continue
mins = {s: min(ps) for s, ps in src_prices_d.items()}
mn, mx = min(mins.values()), max(mins.values())
spread_pct = (mx - mn) / mn * 100
```

### Interpretation notes

- Title matching is exact (after normalisation) — no fuzzy matching. If a
  retailer writes "HP 15s-fq5000" while another writes "HP 15s-fq5000ua",
  they will not be matched.
- A wider spread means more arbitrage opportunity for price-conscious buyers.
- Products with fewer than 3 retailers are excluded even if they show large
  price differences, to reduce noise from potentially different product
  variants.

---

## Chart 9 — Brand Mix per Retailer

**Output:** `charts/09_retailer_brand_mix.png`
**Function:** `chart_retailer_brand_mix()` — `scripts/generate_charts.py:365`

### What it shows

A 100% stacked bar chart. For each retailer (sorted by total listing count
descending), the percentage of listings belonging to each of the seven brands
plus `"Other"`. Lets you see specialisation and diversification at a glance.

### Columns used

| Column | Role |
|---|---|
| `source` | Retailer |
| `title` | Brand detected via `detect_brand()` |

### Calculation

```python
src_brand = defaultdict(Counter)
for _, p, r in priced:
    b = detect_brand(r["title"])
    src_brand[r["source"]][b] += 1
```

Counts are normalised to percentages for each retailer before stacking.

### Colour mapping

Each of the seven brands has a fixed colour taken from the shared `PALETTE`.
`"Other"` is rendered in neutral grey (`#9CA3AF`).

---

## Chart 10 — Average Price: Retailer × Brand

**Output:** `charts/10_price_heatmap.png`
**Function:** `chart_price_heatmap()` — `scripts/generate_charts.py:403`

### What it shows

A colour heatmap with **retailers on the y-axis** and **brands on the
x-axis**. Each cell contains the average `price_azn` for that combination,
coloured on a yellow-orange-red (`YlOrRd`) scale where darker red = higher
price. Empty cells (white/NaN) mean the retailer carries no listings for
that brand.

### Columns used

| Column | Role |
|---|---|
| `source` | Heatmap row |
| `title` | Brand detection for heatmap column |
| `price_azn` | Averaged per cell |

### Calculation

```python
matrix[src][b].append(p)     # accumulate
data_arr[i, j] = statistics.mean(matrix[src][b])   # average
```

Cells with no data remain `np.nan` and are rendered as blank by `imshow`.

### Colour scale

`matplotlib`'s `YlOrRd` continuous colourmap. The scale is set automatically
from the min to max non-NaN value in the matrix. Cell text is black for values
below 4,000 AZN and white for 4,000+ to maintain contrast against the dark
red cells.

### Interpretation notes

- Each cell represents the **average price of all listings** from that
  retailer × brand combination, not a specific model's price.
- A darker cell relative to the same brand's row does not necessarily mean
  the retailer is more expensive — it may simply carry a higher proportion
  of premium models within that brand.
- To determine true competitiveness for a specific product, use Chart 8
  (price spread).

---

## Reproducing the Charts

```bash
# Ensure data/data.csv exists (run combine.py first if needed)
python3 scripts/generate_charts.py
```

Output files are written to `charts/`. Existing files are overwritten.

### Changing the DPI

Edit the `save()` helper at `scripts/generate_charts.py:77`:

```python
fig.savefig(path, dpi=150, ...)   # change 150 to desired value
```

### Adding a new chart

1. Write a new function `chart_<name>(priced)` following the same pattern:
   build the figure, call `save(fig, "<NN>_<name>.png")`.
2. Add the call to the `if __name__ == "__main__":` block.

### Changing the brand list

Edit `BRANDS` at `scripts/generate_charts.py:55`. The `detect_brand()`
function checks brands in list order — put more specific brands before
substrings that could accidentally match (e.g. keep `"MSI"` before any
brand whose name contains "MSI").
