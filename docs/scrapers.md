# Scraper Reference

Each scraper targets one retailer, discovers all pages, parses product cards, and
writes a CSV to `data/`. This document covers the technical specifics of every
scraper: the request strategy, pagination logic, HTML selectors, price-parsing
rules, and any site-specific quirks.

---

## 1. soliton.az — `scripts/soliton.py`

| Property | Value |
|---|---|
| **Output** | `data/soliton.csv` |
| **Rows (Feb 2026)** | 68 |
| **Platform** | Custom PHP |
| **Request method** | POST AJAX |

**Endpoint:**
```
POST https://soliton.az/ajax-requests.php
Content-Type: application/x-www-form-urlencoded
Body: action=loadProducts&sectionID=66&brandID=0&offset={n}&limit=15&sorting=
```

**Pagination:**
Offset-based. Each response contains JSON `{html, hasMore, totalCount, loadedCount}`.
Iteration continues while `hasMore` is `true`, incrementing `offset` by 15 each time.

**Card selector:** `div.product-item`

**Price fields:**
- `data-price` attribute → original price
- `.prodPrice .creditPrice` → credit/instalment price

**Price format:** Plain float (e.g. `849.0`).

**Notable fields:**
`monthly_6_azn`, `monthly_12_azn`, `monthly_18_azn` — extracted from instalment
table inside the card lightbox; `data_filters` — raw filter string for specs.

---

## 2. kontakt.az — `scripts/kontakt.py`

| Property | Value |
|---|---|
| **Output** | `data/kontakt.csv` |
| **Rows (Feb 2026)** | 258 |
| **Platform** | Magento 2 |
| **Request method** | GET |

**Category URL:** `https://kontakt.az/notbuk-ve-kompyuterler/komputerler/notbuklar?p={page}`

**Pagination:**
`?p=` query parameter. Last page discovered from the maximum numeric `href` in
`.pages-items a` pagination links.

**Card selector:** `div.prodItem.product-item[data-gtm]`

**GTM data:** Product metadata (id, sku, name, brand, category) is encoded as JSON
in the `data-gtm` attribute of each card:
```python
meta = json.loads(card["data-gtm"])
```

**Price selectors:**
- Old price: `div.prodItem__prices i` → struck-through original
- Current price: `div.prodItem__prices b` → selling price

**Price format:** Azerbaijani locale — `"2.399,99 ₼"` where `.` is the thousands
separator and `,` is the decimal separator.
```python
cleaned = text.replace("₼","").replace(".", "").replace(",", ".")
# "2.399,99" → "239999" (wrong) — the function removes the period first then
# interprets remaining digits: "2399.99"
```

---

## 3. aztechshop.az — `scripts/aztechshop.py`

| Property | Value |
|---|---|
| **Output** | `data/aztechshop.csv` |
| **Rows (Feb 2026)** | 154 |
| **Platform** | OpenCart |
| **Request method** | GET |

**Category URL:** `https://aztechshop.az/noutbuklar/?page={page}`

**Pagination:**
`ul.pagination` with a `>|` last-page link. Max page extracted from
`/page/(\d+)` in all `a[href]` within the pagination element.

**Card selector:** `div.product-thumb.uni-item`

**Price data attributes on `.product-thumb__price`:**
| Attribute | Meaning |
|---|---|
| `data-price` | Original price |
| `data-special` | Discounted price (`0` = no discount) |
| `data-diff` | Discount amount (absolute) |

**Logic:**
```python
if special > 0:
    price_azn = special
    old_price_azn = original
else:
    price_azn = original
```

**Product ID:** `button[data-pid]` — the add-to-cart button.

---

## 4. irshad.az — `scripts/irshad.py`

| Property | Value |
|---|---|
| **Output** | `data/irshad.csv` |
| **Rows (Feb 2026)** | 414 |
| **Platform** | Laravel |
| **Request method** | GET (AJAX with CSRF) |

**Session bootstrap:**
irshad.az uses Laravel CSRF protection. The scraper performs a two-step init:
1. Fetches the main category page with a `CookieJar`-backed opener to acquire
   the session cookie.
2. Extracts the CSRF token from `<meta name="csrf-token" content="...">`.
3. Passes the token as `X-CSRF-TOKEN` header and the session cookie on all
   subsequent AJAX requests.

```python
cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
```

**AJAX endpoint:**
```
GET https://irshad.az/az/list-products/notbuk-planset-ve-komputer-texnikasi/notbuklar
    ?q=&price_from=&price_to=&sort=first_pinned&page={n}
Headers: X-CSRF-TOKEN: <token>
         X-Requested-With: XMLHttpRequest
```

**Pagination:**
"Load more" style — stop when `#loadMore[data-page]` is absent in the response.

**Card selector:** `div.product`

**Multi-variant cards:** A single card can represent multiple colour/storage
variants. The scraper uses the first visible price block and the first product
link per card.

**Price selectors:**
- `.product__price__current .old-price` → original
- `.product__price__current .new-price` → discounted

**Field name difference:** Uses `product_code` rather than `product_id`.

---

## 5. notecomp.az — `scripts/notecomp.py`

| Property | Value |
|---|---|
| **Output** | `data/notecomp.csv` |
| **Rows (Feb 2026)** | 1,796 |
| **Platform** | OpenCart |
| **Request method** | GET |

**Category URL:** `https://notecomp.az/noutbuklar?page={page}`

**Pagination:** `ul.pagination` — max page from all `a[href]` numeric values;
`>|` last-page shortcut also present.

**Card selector:** `div.product-thumb`

**Product ID extraction:**
No explicit `id` attribute on cards. Extracted from the CSS class name of the
price span:
```python
# class="price_no_format_1234" or "special_no_format_1234"
m = re.search(r"(?:price_no_format|special_no_format)_(\d+)", cls_str)
```

**Price format:** `"1,033AZN"` — comma is the thousands separator.
```python
text.replace("AZN","").replace(",","")  # "1033" → 1033.0
```

**Discount badge:** `div.sticker-ns.procent-skidka` contains the percent string.

**New badge:** `div.sticker-ns.newproduct` → stored as `is_new = True`.

---

## 6. mgstore.az — `scripts/mgstore.py`

| Property | Value |
|---|---|
| **Output** | `data/mgstore.csv` |
| **Rows (Feb 2026)** | 100 |
| **Platform** | Magento 2 (identical to kontakt.az) |
| **Request method** | GET |

**Category URL:** `https://mgstore.az/notbuk-ve-kompyuterler/kompyuterler/notbuklar?p={page}`

All parsing logic is identical to `kontakt.py`. The only structural difference
is that the `brand` field in the GTM JSON is empty for mgstore.az products.

---

## 7. bakuelectronics.az — `scripts/bakuelectronics.py`

| Property | Value |
|---|---|
| **Output** | `data/bakuelectronics.csv` |
| **Rows (Feb 2026)** | 317 |
| **Platform** | Next.js (SSR) |
| **Request method** | GET |

**Category URL:** `https://www.bakuelectronics.az/catalog/noutbuklar-komputerler-planshetler/noutbuklar?page={page}`

**Data source:** All product data is embedded in the page as `__NEXT_DATA__` JSON —
no HTML parsing required:
```python
m = re.search(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    html, re.DOTALL
)
data = json.loads(m.group(1))
items = data["props"]["pageProps"]["products"]["products"]["items"]
```

**Pagination:**
`total` and `size` fields in the JSON → `last_page = math.ceil(total / size)`.

**Price fields:**
| JSON key | Meaning |
|---|---|
| `price` | Original (pre-discount) price |
| `discounted_price` | Actual selling price |
| `discount` | Absolute discount amount |

**Note for combine.py:** `discounted_price` is mapped to `price_azn`; `price`
(the original) is mapped to `old_price_azn` in the unified schema.

---

## 8. techbar.az — `scripts/techbar.py`

| Property | Value |
|---|---|
| **Output** | `data/techbar.csv` |
| **Rows (Feb 2026)** | 155 |
| **Platform** | WooCommerce |
| **Request method** | GET |

**URLs:**
- Page 1: `https://techbar.az/noutbuklar/`
- Page N: `https://techbar.az/noutbuklar/page/{N}/`

**Pagination:** `a.page-numbers` links → max `/page/(\d+)/` value.

**Card selector:** `div.wd-product[data-id]`

**Price selectors (WooCommerce standard):**
- Old: `del .woocommerce-Price-amount bdi`
- Current: `ins .woocommerce-Price-amount bdi`
- Single (no discount): `.woocommerce-Price-amount bdi`

**Price format:** `"2,279.00 ₼"` — comma is the thousands separator.
```python
text.replace("₼","").replace(",","")  # "2279.00" → 2279.0
```

---

## 9. birmarket.az — `scripts/birmarket.py`

| Property | Value |
|---|---|
| **Output** | `data/birmarket.csv` |
| **Rows (Feb 2026)** | 733 |
| **Platform** | Nuxt.js (SSR) |
| **Request method** | GET |

**Category URL:** `https://birmarket.az/categories/16-noutbuklar?page={page}`

**Auth cookie required:**
```
Cookie: auth.strategy=local; cityId=1; citySelected=true
```
Without this cookie the site returns prices for Baku; the cookie pins the city.

**Pagination:** `a[href*="categories/16-noutbuklar?page="]` links → max `page=(\d+)`.

**Card selector:** `div.MPProductItem[data-product-id]`

**Price extraction — combined span trick:**
Each card has `span.flex.flex-col` containing both prices as concatenated text,
plus `span.line-through` for the old price. Current price is isolated by
subtracting the old price text:
```python
full_text = price_span.get_text(" ", strip=True)
old_text  = old_span.get_text(strip=True) if old_span else ""
cur_text  = full_text.replace(old_text, "").strip() if old_text else full_text
```

**Price format:** `"1 039.00 ₼"` — space is the thousands separator.

---

## 10. compstore.az — `scripts/compstore.py`

| Property | Value |
|---|---|
| **Output** | `data/compstore.csv` |
| **Rows (Feb 2026)** | 2,124 |
| **Platform** | Custom PHP CMS |
| **Request method** | GET |

**Category URL:**
`https://compstore.az/kateqoriya/noutbuki.html?action=yes&taxonomy_id=91&taxonomy_page=kateqoriya&s={page}`

**Pagination:** `ul.pagination a[href*="s="]` → max `s=(\d+)` → 89 pages.

**Card selector:** `li.product` → `article.product-inner[data-id]`

**Price:** `span.final-price` — plain integer (e.g. `1899`). No old-price field
on listing pages for this site.

**Monthly badge:** `div.product-badge` → text `"121₼ ayda"` → regex extracts `121`.

---

## 11. ctrl.az — `scripts/ctrl.py`

| Property | Value |
|---|---|
| **Output** | `data/ctrl.csv` |
| **Rows (Feb 2026)** | 21 |
| **Platform** | WordPress + Porto WooCommerce theme |
| **Request method** | POST |

**Endpoint:**
```
POST https://ctrl.az/product-tag/notebooklar/page/{N}/
Body: portoajax=true&load_posts_only=true
```
The Porto theme AJAX payload strips the full page shell and returns just the
product listing HTML fragment.

**Pagination:** `ul.page-numbers a[href*="/page/"]` → max `/page/(\d+)/`.

**Card selector:** `li.product`

**Product ID:** Extracted from the `li` element's class list: `post-{id}`.

**Price format:** `"900,00 ₼"` — comma is the decimal separator (European locale).
```python
text.replace(",", ".")  # "900.00"
```

---

## 12. brothers.az — `scripts/brothers.py`

| Property | Value |
|---|---|
| **Output** | `data/brothers.csv` |
| **Rows (Feb 2026)** | 1,527 |
| **Platform** | Custom PHP CMS |
| **Request method** | GET |

**URL:** `https://brothers.az/product/ucuz-qiymete-notebooklar`

**No pagination** — all 1,527 products are server-rendered on a single ~10 MB
HTML page. The scraper fetches one URL with a 60-second timeout.

**Card selector:** `article.single_product.owl-item-slide`
(excludes template card with class `product_example hide`).

Each article contains two internal sections for grid and list display.
Only `div.grid_content` is parsed to avoid processing duplicate data.

**Product ID:** Extracted from URL path: `/product_read/{id}/slug`.

**Price format:** `"2,219 ₼"` — comma is the thousands separator.
```python
text.replace("₼","").replace(",","")  # "2219" → 2219.0
```

**Old price:** Commented out in the HTML source — not available.

---

## 13. qiymeti.net — `scripts/qiymeti.py`

| Property | Value |
|---|---|
| **Output** | `data/qiymeti.csv` |
| **Rows (Feb 2026)** | 506 |
| **Platform** | WordPress (custom AJAX action) |
| **Request method** | GET |

**AJAX endpoint:**
```
GET https://qiymeti.net/wp-admin/admin-ajax.php
    ?sehife={page}&action=print_filters_and_products&product_type=notebook
```

**Pagination:**
Max numeric value of `div.pagination .page-numbers` text elements.
Also confirmed via `var productsCount = 506` embedded in the page JS.

**Card selector:** `div.product[data-product-id]`

**Price format:** `"1 239 ,00 AZN"` — space is the thousands separator;
comma is the decimal separator.
```python
text.replace("AZN","").replace(" ","").replace(",",".")
# "1 239 ,00" → "1239.00"
```

**Specs field:** `div.specifications` — rich comma-separated spec string
(screen size, CPU series, RAM, storage) directly usable for filtering.

---

## 14. icomp.az — `scripts/icomp.py`

| Property | Value |
|---|---|
| **Output** | `data/icomp.csv` |
| **Rows (Feb 2026)** | 142 |
| **Platform** | Custom PHP CMS (same as compstore.az) |
| **Request method** | GET |

**Category URL:**
`https://icomp.az/kateqoriya/noutbuklar-ultrabuklar.html?action=yes&taxonomy_id=406&taxonomy_page=kateqoriya&s={page}`

**Key difference from compstore.az:**
icomp.az exposes both `span.final-price` (current) and `span.sale-price`
(original/crossed-out) — discount data is available on every card.

**Pagination:** Same as compstore.az — max `s=` from `ul.pagination a` links → 6 pages.

**Card selector:** `div.product[data-id]` (not `li.product` as on compstore.az).

---

## 15. mimelon.com — `scripts/mimelon.py`

| Property | Value |
|---|---|
| **Output** | `data/mimelon.csv` |
| **Rows (Feb 2026)** | 174 |
| **Platform** | CodeIgniter |
| **Request method** | GET |

**URLs:**
- Page 1: `https://mimelon.com/az/notebooklar`
- Page N: `https://mimelon.com/az/notebooklar/{N}`

**Pagination:** `div.pagination.main-pagination a[data-ci-pagination-page]` →
max numeric value → 9 pages.

**Card selector:** `div.product.owl-item-slide`
Template card (with classes `hide product_example`) is skipped.

**Product ID & URL:** `a.dataLayerProductClick[data-id]` and `[href]`.

**Price format:** `"979m"` — `m` is rendered by a `<i class="fa fa-azn">` icon tag
whose text content is `"m"`. Stripped with:
```python
re.sub(r"[^\d\s,\.]", "", text).strip().replace(" ","").replace(",",".")
```

---

## 16. bytelecom.az — `scripts/bytelecom.py`

| Property | Value |
|---|---|
| **Output** | `data/bytelecom.csv` |
| **Rows (Feb 2026)** | 59 |
| **Platform** | Laravel + Livewire |
| **Request method** | GET |

**Category URL:** `https://bytelecom.az/az/category/noutbuklar?page={page}`

Although the pagination buttons use `wire:click` Livewire events in-browser,
the server renders the full page for standard GET requests with `?page=N`.

**Pagination:** `ul.pagination button[wire:click*="gotoPage"]` →
regex `gotoPage\((\d+)` → max value → 4 pages.

**Product ID:** `button.favourite-product[wire:click]` →
regex `toggleWishlist\((\d+)\)`.

**Price selectors:**
- `h6.discount-price` → original (crossed-out) price
- `h5.price` → current selling price

**Price format:** `"₼ 2,699.00"` — comma is thousands separator.
```python
text.replace("₼","").replace(",","")  # " 2699.00" → 2699.0
```

**Badges:** `div.badge-item p` — instalment labels such as
"İlkin ödənişsiz və Faizsiz" (interest-free) and "Taksitlə al" (buy on instalment).

---

## Price Format Summary

| Format example | Thousands sep | Decimal sep | Sites |
|---|---|---|---|
| `2.399,99 ₼` | `.` | `,` | kontakt.az, mgstore.az |
| `1,033AZN` | `,` | none | notecomp.az |
| `2,279.00 ₼` | `,` | `.` | techbar.az, bytelecom.az |
| `1 039.00 ₼` | ` ` (space) | `.` | birmarket.az |
| `1 239 ,00 AZN` | ` ` (space) | `,` | qiymeti.net |
| `900,00 ₼` | none | `,` | ctrl.az |
| `979m` | none | none | mimelon.com (`m` = AZN icon) |
| `2,219 ₼` | `,` | none | brothers.az |
| `1899` (integer) | none | none | compstore.az, icomp.az |
| `849.0` (float) | none | `.` | soliton.az, bakuelectronics.az |
