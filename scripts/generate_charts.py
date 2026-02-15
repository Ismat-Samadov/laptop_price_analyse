"""
Business Intelligence Charts — Azerbaijan Laptop Market
Reads data/data.csv and saves all charts to charts/.
"""

import csv
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "data.csv"
CHARTS_DIR = ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────────
PALETTE = [
    "#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED",
    "#0891B2", "#BE185D", "#65A30D", "#EA580C", "#0F766E",
    "#6D28D9", "#B45309", "#1D4ED8", "#15803D", "#9333EA",
    "#C2410C",
]
ACCENT   = "#2563EB"
GRID_CLR = "#E5E7EB"
BG_CLR   = "#FAFAFA"

plt.rcParams.update({
    "figure.facecolor":  BG_CLR,
    "axes.facecolor":    BG_CLR,
    "axes.edgecolor":    "#D1D5DB",
    "axes.grid":         True,
    "grid.color":        GRID_CLR,
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

BRANDS = ["ASUS","HP","Lenovo","Acer","MSI","Dell","Apple"]

# ── Load data ────────────────────────────────────────────────────────────────
def load():
    rows = list(csv.DictReader(open(DATA_FILE, encoding="utf-8")))
    priced = []
    for r in rows:
        try:
            p = float(r["price_azn"])
            if p > 0:
                priced.append((r["source"], p, r))
        except:
            pass
    return rows, priced

def detect_brand(title: str) -> str:
    t = title.upper()
    for b in BRANDS:
        if b.upper() in t:
            return b
    return "Other"

def save(fig, name: str):
    path = CHARTS_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_CLR)
    plt.close(fig)
    print(f"  Saved {path.name}")


# ════════════════════════════════════════════════════════════════════════════
# Chart 1 — Catalog Size by Retailer
# ════════════════════════════════════════════════════════════════════════════
def chart_catalog_size(priced):
    src_count = Counter(src for src, _, _ in priced)
    labels, vals = zip(*sorted(src_count.items(), key=lambda x: x[1]))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, vals, color=ACCENT, height=0.6)
    ax.bar_label(bars, fmt="%d", padding=4, fontsize=9, color="#374151")
    ax.set_xlabel("Number of Listings")
    ax.set_title("Chart 1 — Catalog Size by Retailer\nHow many laptop listings each retailer carries")
    ax.set_xlim(0, max(vals) * 1.15)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save(fig, "01_catalog_size.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 2 — Average & Median Price by Retailer
# ════════════════════════════════════════════════════════════════════════════
def chart_price_positioning(priced):
    src_prices = defaultdict(list)
    for src, p, _ in priced:
        src_prices[src].append(p)

    data = [(src, statistics.mean(ps), statistics.median(ps))
            for src, ps in src_prices.items()]
    data.sort(key=lambda x: x[1])

    labels = [d[0] for d in data]
    avgs   = [d[1] for d in data]
    medns  = [d[2] for d in data]

    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(12, 6))
    b1 = ax.bar(x - w/2, avgs,  w, label="Average Price",  color=PALETTE[0], alpha=0.9)
    b2 = ax.bar(x + w/2, medns, w, label="Median Price",   color=PALETTE[1], alpha=0.9)
    ax.bar_label(b1, fmt="%.0f", padding=3, fontsize=8, color="#374151")
    ax.bar_label(b2, fmt="%.0f", padding=3, fontsize=8, color="#374151")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Price (AZN)")
    ax.set_title("Chart 2 — Price Positioning by Retailer\nAverage vs. Median listing price per retailer")
    ax.legend()
    fig.tight_layout()
    save(fig, "02_price_positioning.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 3 — Market Price Distribution
# ════════════════════════════════════════════════════════════════════════════
def chart_price_distribution(priced):
    brackets = ["Under 500","500–999","1,000–1,999","2,000–2,999","3,000–4,999","5,000+"]
    limits   = [500, 1000, 2000, 3000, 5000, float("inf")]
    counts   = [0] * 6

    for _, p, _ in priced:
        for i, lim in enumerate(limits):
            if p < lim:
                counts[i] += 1
                break

    total = sum(counts)
    pcts  = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(brackets, counts, color=PALETTE[:6], width=0.6, edgecolor="white", linewidth=0.8)
    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f"{pct:.1f}%", ha="center", va="bottom", fontsize=10, color="#374151")
    ax.set_ylabel("Number of Listings")
    ax.set_xlabel("Price Range (AZN)")
    ax.set_title("Chart 3 — Market Price Distribution\nHow the market splits across price segments")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    save(fig, "03_price_distribution.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 4 — Brand Market Share by Listing Volume
# ════════════════════════════════════════════════════════════════════════════
def chart_brand_share(priced):
    brand_count = Counter(detect_brand(r["title"]) for _, _, r in priced)
    # Exclude "Other" for clarity, sort
    data = [(b, brand_count[b]) for b in BRANDS if brand_count[b] > 0]
    data.sort(key=lambda x: x[1])
    labels, vals = zip(*data)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(labels, vals, color=PALETTE[:len(labels)], height=0.55)
    ax.bar_label(bars, fmt="%d", padding=4, fontsize=9)
    ax.set_xlabel("Number of Listings")
    ax.set_title("Chart 4 — Brand Market Share by Listing Volume\nWhich brands dominate the Azerbaijani laptop market")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(vals) * 1.15)
    fig.tight_layout()
    save(fig, "04_brand_share.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 5 — Average Price by Brand
# ════════════════════════════════════════════════════════════════════════════
def chart_brand_price(priced):
    brand_prices = defaultdict(list)
    for _, p, r in priced:
        b = detect_brand(r["title"])
        if b != "Other":
            brand_prices[b].append(p)

    data = [(b, statistics.mean(ps), statistics.median(ps))
            for b, ps in brand_prices.items()]
    data.sort(key=lambda x: x[1])
    labels = [d[0] for d in data]
    avgs   = [d[1] for d in data]
    medns  = [d[2] for d in data]

    x = np.arange(len(labels))
    w = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(x - w/2, avgs,  w, label="Average Price", color=PALETTE[0], alpha=0.9)
    b2 = ax.bar(x + w/2, medns, w, label="Median Price",  color=PALETTE[1], alpha=0.9)
    ax.bar_label(b1, fmt="%.0f", padding=3, fontsize=9)
    ax.bar_label(b2, fmt="%.0f", padding=3, fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Price (AZN)")
    ax.set_title("Chart 5 — Average Price by Brand\nBrand price tier positioning in the market")
    ax.legend()
    fig.tight_layout()
    save(fig, "05_brand_price.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 6 — Price Segment Mix per Brand (stacked bar)
# ════════════════════════════════════════════════════════════════════════════
def chart_brand_segments(priced):
    seg_labels = ["Under 1,000","1,000–1,999","2,000–2,999","3,000+"]
    brand_segs  = {b: [0, 0, 0, 0] for b in BRANDS}

    for _, p, r in priced:
        b = detect_brand(r["title"])
        if b not in brand_segs:
            continue
        if p < 1000:        brand_segs[b][0] += 1
        elif p < 2000:      brand_segs[b][1] += 1
        elif p < 3000:      brand_segs[b][2] += 1
        else:               brand_segs[b][3] += 1

    # Only brands with data, sort by total
    brands_ord = sorted(
        [b for b in BRANDS if sum(brand_segs[b]) > 0],
        key=lambda b: sum(brand_segs[b])
    )
    totals = [sum(brand_segs[b]) for b in brands_ord]

    # Normalise to percentage
    seg_pcts = []
    for seg_i in range(4):
        seg_pcts.append([brand_segs[b][seg_i] / sum(brand_segs[b]) * 100 for b in brands_ord])

    seg_colors = ["#16A34A", "#2563EB", "#D97706", "#DC2626"]
    x = np.arange(len(brands_ord))

    fig, ax = plt.subplots(figsize=(11, 6))
    bottoms = [0] * len(brands_ord)
    for i, (seg, color) in enumerate(zip(seg_labels, seg_colors)):
        ax.bar(x, seg_pcts[i], bottom=bottoms, label=seg, color=color, alpha=0.88, width=0.6)
        # Label segments > 10%
        for j, pct in enumerate(seg_pcts[i]):
            if pct > 8:
                ax.text(x[j], bottoms[j] + pct / 2, f"{pct:.0f}%",
                        ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        bottoms = [b + v for b, v in zip(bottoms, seg_pcts[i])]

    ax.set_xticks(x)
    ax.set_xticklabels(brands_ord)
    ax.set_ylabel("Share of Listings (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Chart 6 — Price Segment Mix per Brand\nBudget / Mid-range / Upper / Premium split by brand")
    ax.legend(loc="upper right")
    fig.tight_layout()
    save(fig, "06_brand_segments.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 7 — Discount Frequency & Depth by Retailer
# ════════════════════════════════════════════════════════════════════════════
def chart_discounts(priced):
    src_total  = Counter(src for src, _, _ in priced)
    src_disc   = defaultdict(list)

    for src, p, r in priced:
        try:
            d  = float(r["discount_azn"])
            op = float(r["old_price_azn"])
            if d > 0 and op > 0:
                src_disc[src].append(d / op * 100)
        except:
            pass

    # Only retailers that have discounts
    disc_srcs = sorted(src_disc.keys(), key=lambda s: statistics.mean(src_disc[s]))
    freq  = [len(src_disc[s]) / src_total[s] * 100 for s in disc_srcs]
    depth = [statistics.mean(src_disc[s]) for s in disc_srcs]

    x = np.arange(len(disc_srcs))
    w = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 6))
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - w/2, freq,  w, label="% Listings Discounted", color=PALETTE[0], alpha=0.9)
    b2 = ax2.bar(x + w/2, depth, w, label="Avg Discount %",         color=PALETTE[2], alpha=0.9)

    ax1.set_xticks(x)
    ax1.set_xticklabels(disc_srcs, rotation=30, ha="right")
    ax1.set_ylabel("Share of Discounted Listings (%)", color=PALETTE[0])
    ax2.set_ylabel("Average Discount Depth (%)", color=PALETTE[2])
    ax1.set_title("Chart 7 — Discount Strategy by Retailer\nHow aggressively each retailer discounts its catalog")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    ax1.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "07_discount_strategy.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 8 — Cross-Retailer Price Spread on Identical Models
# ════════════════════════════════════════════════════════════════════════════
def chart_price_spread(priced):
    def clean(t):
        return re.sub(r"\s+", " ", t.lower().strip())

    title_map = defaultdict(lambda: defaultdict(list))
    for src, p, r in priced:
        title_map[clean(r["title"])][src].append(p)

    spreads = []
    for title, src_prices_d in title_map.items():
        if len(src_prices_d) < 3:
            continue
        mins = {s: min(ps) for s, ps in src_prices_d.items()}
        mn, mx = min(mins.values()), max(mins.values())
        if mn > 0:
            spreads.append((title, mn, mx, (mx - mn) / mn * 100, len(mins)))

    spreads.sort(key=lambda x: -x[3])
    top = spreads[:12]

    labels  = [t[0][:40] + "…" if len(t[0]) > 40 else t[0] for t in top]
    mins_v  = [t[1] for t in top]
    maxs_v  = [t[2] for t in top]
    pcts    = [t[3] for t in top]

    y = np.arange(len(top))

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(y, maxs_v, color="#DC2626", alpha=0.5, height=0.5, label="Highest Price")
    ax.barh(y, mins_v, color="#16A34A", alpha=0.9, height=0.5, label="Lowest Price")
    for i, (mn, pct) in enumerate(zip(mins_v, pcts)):
        ax.text(maxs_v[i] + 30, i, f"+{pct:.0f}%", va="center", fontsize=9, color="#374151")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Price (AZN)")
    ax.set_title("Chart 8 — Price Spread on Identical Models Across Retailers\nGreen = cheapest, Red = most expensive for same product")
    ax.legend()
    fig.tight_layout()
    save(fig, "08_price_spread.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 9 — Brand Mix per Retailer (stacked bar)
# ════════════════════════════════════════════════════════════════════════════
def chart_retailer_brand_mix(priced):
    src_brand = defaultdict(Counter)
    for _, p, r in priced:
        b = detect_brand(r["title"])
        src_brand[r["source"]][b] += 1

    top_brands = BRANDS  # 7 brands + other
    # Sort retailers by total listings descending
    srcs = sorted(src_brand.keys(), key=lambda s: sum(src_brand[s].values()), reverse=True)

    brand_colors = {b: PALETTE[i] for i, b in enumerate(top_brands)}
    brand_colors["Other"] = "#9CA3AF"

    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(srcs))
    bottoms = np.zeros(len(srcs))

    all_brands = top_brands + ["Other"]
    for b in all_brands:
        vals = np.array([src_brand[s][b] for s in srcs], dtype=float)
        totals = np.array([sum(src_brand[s].values()) for s in srcs], dtype=float)
        pcts = np.where(totals > 0, vals / totals * 100, 0)
        ax.bar(x, pcts, bottom=bottoms, label=b, color=brand_colors[b], width=0.65, alpha=0.9)
        bottoms += pcts

    ax.set_xticks(x)
    ax.set_xticklabels(srcs, rotation=35, ha="right")
    ax.set_ylabel("Share of Listings (%)")
    ax.set_ylim(0, 115)
    ax.set_title("Chart 9 — Brand Mix per Retailer\nWhich brands each retailer focuses on")
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    save(fig, "09_retailer_brand_mix.png")


# ════════════════════════════════════════════════════════════════════════════
# Chart 10 — Market Price Heatmap: Retailer × Brand (avg price)
# ════════════════════════════════════════════════════════════════════════════
def chart_price_heatmap(priced):
    top_brands = ["ASUS","HP","Lenovo","Acer","MSI","Dell","Apple"]
    srcs = sorted(set(src for src, _, _ in priced))

    matrix = defaultdict(lambda: defaultdict(list))
    for src, p, r in priced:
        b = detect_brand(r["title"])
        if b in top_brands:
            matrix[src][b].append(p)

    # Build 2D array
    data_arr = np.full((len(srcs), len(top_brands)), np.nan)
    for i, src in enumerate(srcs):
        for j, b in enumerate(top_brands):
            if matrix[src][b]:
                data_arr[i, j] = statistics.mean(matrix[src][b])

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(data_arr, cmap="YlOrRd", aspect="auto", interpolation="nearest")

    ax.set_xticks(np.arange(len(top_brands)))
    ax.set_yticks(np.arange(len(srcs)))
    ax.set_xticklabels(top_brands, fontsize=11)
    ax.set_yticklabels(srcs, fontsize=10)

    for i in range(len(srcs)):
        for j in range(len(top_brands)):
            val = data_arr[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        fontsize=9, color="black" if val < 4000 else "white")

    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Avg Price (AZN)", fontsize=10)
    ax.set_title("Chart 10 — Average Price: Retailer × Brand\nWhere each retailer sits for each brand (AZN)")
    fig.tight_layout()
    save(fig, "10_price_heatmap.png")


# ════════════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Loading {DATA_FILE} ...")
    rows, priced = load()
    print(f"  {len(rows)} total rows, {len(priced)} with valid prices\n")

    print("Generating charts:")
    chart_catalog_size(priced)
    chart_price_positioning(priced)
    chart_price_distribution(priced)
    chart_brand_share(priced)
    chart_brand_price(priced)
    chart_brand_segments(priced)
    chart_discounts(priced)
    chart_price_spread(priced)
    chart_retailer_brand_mix(priced)
    chart_price_heatmap(priced)

    print(f"\nAll charts saved to {CHARTS_DIR}/")
