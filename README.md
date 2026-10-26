# Global Sources Scraper (Python): products, FOB prices, MOQ and verified suppliers as JSON

Search Global Sources (globalsources.com) from Python and get every product as a JSON row: FOB price range, MOQ, lead time, FOB port, category, and the supplier behind it with its P1-P6 star ranking, years on Global Sources, business types, verified-manufacturer badge and trade-show history. Filter by supplier country, verified factories, ranking, certificates, OEM and price before anything is saved. No browser, no Global Sources account, no API key from Global Sources.

> I built this actor; it's a paid tool on Apify ($1.50 per 1,000 products, with Apify's free trial credit). Store page: https://apify.com/rel8ble/global-sources-scraper

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/global-sources-scraper").call(run_input={
    "searchTerms": ["yoga mat", "bluetooth speaker"],
    "maxResultsPerSearch": 200,
    "verifiedManufacturerOnly": True,
    "maxMoq": 1000,
    "maxPrice": 20,
})

for p in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(p["priceText"], "| MOQ", p["moq"], p["moqUnit"], "|", p["supplierName"], f"P{p['supplierLevel']}", p["supplierLocation"])
```

Get your token at https://console.apify.com/settings/integrations.

## Node.js

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/global-sources-scraper').call({
    searchTerms: ['led light'],
    supplierLocations: ['Vietnam', 'India'],
    minSupplierLevel: 5,
    maxResultsPerSearch: 100,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const p of items) console.log(p.priceMin, p.moq, p.supplierName, p.supplierYearsOnGlobalSources, p.url);
```

## Input

| Field | Default | Description |
|---|---|---|
| `searchTerms` | - | Product keywords (`"led light"`) or Global Sources search URLs |
| `maxResultsPerSearch` | 100 | Products saved per search term. 0 = everything (up to 20,000) |
| `minPrice` / `maxPrice` | - | FOB unit price range in USD; products outside it are skipped and not charged |
| `maxMoq` | - | Only products whose minimum order quantity is at or below this |
| `verifiedManufacturerOnly` | false | Only suppliers verified as factories, not traders |
| `supplierLocations` | - | e.g. `["China", "Vietnam", "India", "Taiwan"]` |
| `businessTypes` | - | `"Manufacturer"`, `"Exporter"`, `"Wholesaler"`, `"Agent"` ... |
| `minSupplierLevel` | - | Star ranking P1-P6; `5` keeps P5 and P6 |
| `minYearsInBusiness` | - | Uses Global Sources' year buckets |
| `productCertifications` / `companyCertifications` | - | e.g. `["CE", "ROHS"]`, `["ISO 9001:2015", "BSCI"]` |
| `fobPorts` | - | e.g. `["Shenzhen", "Ningbo"]` |
| `oemOnly` / `tradeShowExhibitorsOnly` | false | OEM / private-label suppliers; suppliers that exhibit at Global Sources shows |
| `includeAds` | true | Keep sponsored listings (flagged `isAd`) |

## What a row looks like

From a real "led light" run on 24 Oct 2026, trimmed (each row has about 45 fields):

```json
{
    "productId": "1230765239",
    "title": "Multi function LED Work Light | Rotatable, Magnetic Base & Rechargeable Spotlight with Multiple Light",
    "url": "https://www.globalsources.com/Work-light/LED-work-light-1230765239p.htm",
    "priceMin": 7.3,
    "priceMax": 7.5,
    "priceType": "PRICE_BY_ORDER_QUANTITY",
    "moq": 100,
    "moqUnit": "Boxes",
    "leadTimeDays": 7,
    "fobPort": "Ningbo",
    "categoryPath": ["Hardware", "Lighting & Electricals", "Industrial Lighting", "Work lights"],
    "supplierName": "Market Union Co. Ltd",
    "supplierUrl": "https://market-union.manufacturer.globalsources.com/",
    "supplierLocation": "China",
    "supplierYearsOnGlobalSources": 4,
    "supplierLevel": 6,
    "supplierBusinessTypes": ["Buying Office", "Trading Company", "Agent"],
    "verifiedSupplier": true,
    "verifiedManufacturer": false,
    "tradeShows": "Exhibited at 2 GS shows"
}
```

## The example: a supplier shortlist that fits your order size

`example.py` searches one keyword, saves every product to `globalsources_products.csv`, drops products whose MOQ is above the quantity you plan to order, and prints one line per supplier: verified factories first, then by star ranking and years on Global Sources, with each supplier's cheapest FOB price.

```bash
pip install -r requirements.txt
APIFY_TOKEN=<YOUR_APIFY_TOKEN> python example.py
```

Output on the 20-row "led light" sample from 24 Oct 2026 (order quantity 1,000):

```
"led light": 20 products, 18 with MOQ <= 1000, 4 from verified manufacturers
FOB 'from' price: min $0.18, median $10.00, max $100.00

factory rank  years  from $   MOQ           supplier
yes     P6    4      10.79    100 pieces    Xiamen Yi Easy Buy Import and Export Trade Group Co.,Ltd
yes     P5    8      7.00     10 pieces     Shenzhen Golden Trees Technology Co., Ltd
yes     P5    4      80.90    1 pieces      Shenzhen JMK Technology Co., Ltd.
yes     P5    3      14.02    1000 pieces   Hitech Industrial Co.,Limited
no      P6    17     10.00    1000 pieces   Jinjiang Jiaxing Group Co. Ltd
no      P6    17     0.48     1000 pieces   Jinjiang Jiaxing Company
...
```

Only 4 of 18 suppliers in that sample are verified factories, which is why `verifiedManufacturerOnly` exists: set it and the filter runs on Global Sources' side, so the traders are never fetched or charged. "led light" is a broad keyword (work lights, string lights and street lights in one list); a narrower term gives a cleaner price spread.

## Pricing and limits

- $1.50 per 1,000 products, no start fee. Products removed by your filters, duplicates and failed requests are not charged.
- Search results only: full spec sheets and per-quantity price tiers are on product pages, which this version does not open.
- Certificates are rarely printed on search cards, so the certificate fields in rows are often empty; the certificate filters still work because Global Sources applies them itself.
- Prices are FOB list prices from the search card; about 5% of suppliers hide prices (`priceMin: null`).
- Lead time and FOB port are filled only when the supplier gives them (about 10% of cards).
- No contact person names, phones or emails are collected.

Comparing with Alibaba? The [Alibaba search scraper](https://github.com/Rel8ble/alibaba-product-scraper-python) returns similar rows for the same keyword.

## Links

- Apify Store: https://apify.com/rel8ble/global-sources-scraper
- Tutorial on dev.to: https://dev.to/rel8ble/finding-verified-factories-on-global-sources-with-python-no-browser-3c77

## License

MIT (this example code). The actor itself is a paid Apify tool.
