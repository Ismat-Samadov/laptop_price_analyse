# Data Schema

This document defines every column in every CSV produced by the project — both
the per-site raw files and the unified `data/data.csv`.

---

## Unified Dataset — `data/data.csv`

Produced by `scripts/combine.py`. Contains one row per listing with a `source`
column identifying the originating retailer.

| Column | Type | Description |
|---|---|---|
| `source` | string | Retailer domain (e.g. `kontakt.az`) |
| `product_id` | string | Site-internal product identifier. May be numeric, alphanumeric, or a timestamp-based code. Empty for sites without an exposed ID. |
| `title` | string | Full product name as displayed on the listing page |
| `url` | string | Absolute URL to the product detail page |
| `price_azn` | float | **Current selling price** in Azerbaijani Manat. For bakuelectronics.az this is the `discounted_price`; for all others it is the primary displayed price. Empty if the site did not return a parseable price. |
| `old_price_azn` | float | Original price before any discount. Empty if the product is not on sale or the retailer does not expose original pricing. |
| `discount_azn` | float | Absolute discount in AZN (`old_price_azn − price_azn`). Computed by the scraper or taken directly from the site's data attribute. |
| `discount_percent` | string | Discount label as shown on the site (e.g. `"-13%"`, `"11%"`). String, not numeric, because formats vary. |
| `brand` | string | Brand name where the retailer exposes it explicitly. Populated for kontakt.az, mgstore.az (numeric brand ID), and soliton.az. Empty for all other sites — use `title` text to infer brand. |
| `specs` | string | Short specification excerpt. Available from aztechshop.az (`description`), compstore.az, icomp.az, kontakt.az, mgstore.az, qiymeti.net, and techbar.az. |
| `availability` | string | Stock/availability status. Populated by aztechshop.az and irshad.az. |
| `label` | string | Pipe-separated badge labels from the listing. Sources: `label` (brothers.az, mimelon.com), `labels` (irshad.az, techbar.az), `badges` (bytelecom.az), `is_new` flag (notecomp.az → `"new"`). |
| `monthly_payment_azn` | float | Representative instalment amount. For soliton.az this is the 12-month plan; for compstore.az and irshad.az it is the site's displayed monthly figure. |
| `rating` | string | Numeric rating (stars). Populated only by bakuelectronics.az. |
| `review_count` | string | Number of customer reviews. Populated only by bakuelectronics.az. |

### Column Coverage by Source

| Source | price | old_price | discount_azn | disc_% | brand | specs | avail | label | monthly | rating |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| soliton.az | ✓ | | ✓ | ✓ | ✓ | | | | ✓ | |
| kontakt.az | ✓ | ✓ | ✓ | | ✓ | ✓ | | | | |
| aztechshop.az | ✓ | ✓ | ✓ | | | ✓ | ✓ | | | |
| irshad.az | ✓ | ✓ | ✓ | | | | ✓ | ✓ | ✓ | |
| notecomp.az | ✓ | ✓ | | ✓ | | | | ✓ | | |
| mgstore.az | ✓ | ✓ | ✓ | | | ✓ | | | | |
| bakuelectronics.az | ✓ | ✓ | ✓ | | | | | | ✓ | ✓ |
| techbar.az | ✓ | ✓ | ✓ | | | ✓ | | ✓ | | |
| birmarket.az | ✓ | ✓ | ✓ | ✓ | | | | | | |
| compstore.az | ✓ | | | | | ✓ | | | ✓ | |
| ctrl.az | ✓ | ✓ | ✓ | ✓ | | | | | | |
| brothers.az | ✓ | | | | | | | ✓ | | |
| qiymeti.net | ✓ | | | | | ✓ | | | | |
| icomp.az | ✓ | ✓ | ✓ | | | ✓ | | | | |
| mimelon.com | ✓ | | | | | | | ✓ | | |
| bytelecom.az | ✓ | ✓ | ✓ | | | | | ✓ | | |

---

## Per-Site Raw Schemas

### `data/soliton.csv`

| Column | Description |
|---|---|
| `product_id` | Internal ID (timestamp-based, e.g. `20260123041324264`) |
| `title` | Product name |
| `brand_id` | Numeric brand ID |
| `url` | Full product URL |
| `price_azn` | Current price |
| `credit_price_azn` | Displayed credit/instalment price |
| `discount_percent` | Discount label (e.g. `"11%"`) |
| `discount_amount_azn` | Absolute discount |
| `monthly_6_azn` | 6-month instalment |
| `monthly_12_azn` | 12-month instalment |
| `monthly_18_azn` | 18-month instalment |
| `special_offers` | Pipe-separated special offer labels |
| `position` | Position in the listing |
| `data_filters` | Raw filter attributes string |

---

### `data/kontakt.csv` / `data/mgstore.csv`

| Column | Description |
|---|---|
| `product_id` | GTM product ID |
| `sku` | Product SKU |
| `title` | Product name |
| `brand` | Brand name (from GTM data; empty for mgstore.az) |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `specs` | Spec excerpt from `.prodItem__wrapText` |
| `category` | Primary category (from GTM) |
| `category2` | Secondary category |
| `category3` | Tertiary category |

---

### `data/aztechshop.csv`

| Column | Description |
|---|---|
| `product_id` | From add-to-cart `data-pid` button |
| `title` | Product name |
| `url` | Full product URL |
| `description` | Short description text |
| `price_azn` | Current price (special if discounted, else original) |
| `old_price_azn` | Original price (only if discounted) |
| `discount_azn` | Absolute discount |
| `availability` | Stock status text |

---

### `data/irshad.csv`

| Column | Description |
|---|---|
| `product_code` | Product code (mapped to `product_id` in unified schema) |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `availability` | Availability status |
| `labels` | Pipe-separated badge labels |
| `monthly_payment_azn` | Monthly instalment amount |

---

### `data/notecomp.csv`

| Column | Description |
|---|---|
| `product_id` | Extracted from price span CSS class |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_percent` | Discount percent label |
| `is_new` | `True` / empty — "new product" badge |

---

### `data/bakuelectronics.csv`

| Column | Description |
|---|---|
| `product_id` | Site internal ID |
| `product_code` | Manufacturer part number |
| `title` | Product name |
| `url` | Full product URL (`/mehsul/{slug}`) |
| `price_azn` | **Original** (pre-discount) price |
| `discounted_price_azn` | **Selling** price (may equal `price_azn` if no discount) |
| `discount_azn` | Absolute discount |
| `monthly_payment_azn` | Monthly instalment |
| `installment_months` | Number of months for instalment plan |
| `rating` | Star rating |
| `review_count` | Number of reviews |
| `quantity` | Stock quantity |
| `is_online` | Whether the product is available online |

> **Important:** In `data/data.csv` `discounted_price_azn` becomes `price_azn`
> and `price_azn` becomes `old_price_azn`.

---

### `data/techbar.csv`

| Column | Description |
|---|---|
| `product_id` | WooCommerce product ID from `data-id` |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `labels` | Pipe-separated product labels |
| `specs` | Short description from `.wd-desc` |

---

### `data/birmarket.csv`

| Column | Description |
|---|---|
| `product_id` | From `data-product-id` attribute |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_percent` | Discount label (e.g. `"-28 %"`) |
| `discount_azn` | Computed discount |

---

### `data/compstore.csv`

| Column | Description |
|---|---|
| `product_id` | From `data-id` attribute on article element |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `monthly_payment_azn` | Monthly instalment badge amount |
| `specs` | Product excerpt from `p.product-excerpt` |

---

### `data/ctrl.csv`

| Column | Description |
|---|---|
| `product_id` | Extracted from `li.post-{id}` class |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `discount_percent` | Discount label from `.onsale` |

---

### `data/brothers.csv`

| Column | Description |
|---|---|
| `product_id` | Extracted from URL path `/product_read/{id}/` |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `label` | Badge text (e.g. `"Yeni"`) |

---

### `data/qiymeti.csv`

| Column | Description |
|---|---|
| `product_id` | From `data-product-id` attribute |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Minimum price across tracked stores |
| `specs` | Comma-separated spec summary |

---

### `data/icomp.csv`

| Column | Description |
|---|---|
| `product_id` | From `data-id` attribute |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `specs` | Spec excerpt from `div.product-excerpt` |

---

### `data/mimelon.csv`

| Column | Description |
|---|---|
| `product_id` | From `a.dataLayerProductClick[data-id]` |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `label` | Badge label (e.g. `"Out of stock"`) |

---

### `data/bytelecom.csv`

| Column | Description |
|---|---|
| `product_id` | From `toggleWishlist({id})` Livewire call |
| `title` | Product name |
| `url` | Full product URL |
| `price_azn` | Current price |
| `old_price_azn` | Original price |
| `discount_azn` | Computed discount |
| `badges` | Pipe-separated instalment/payment badges |
