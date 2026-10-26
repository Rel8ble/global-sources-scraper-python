"""Global Sources sourcing shortlist.

Searches Global Sources for a product keyword, saves every product to
globalsources_products.csv, then prints a supplier shortlist: one line per
supplier whose MOQ fits your order, verified manufacturers first, with the
cheapest FOB price, star ranking (P1-P6) and years on Global Sources.

    pip install -r requirements.txt
    APIFY_TOKEN=<YOUR_APIFY_TOKEN> python example.py
"""
import csv
import os
from collections import defaultdict

from apify_client import ApifyClient

KEYWORD = "led light"
ORDER_QTY = 1000          # the quantity you plan to order; products with a higher MOQ are dropped
MAX_PRODUCTS = 200        # products to fetch (you pay per product saved)

client = ApifyClient(os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>"))
run = client.actor("rel8ble/global-sources-scraper").call(run_input={
    "searchTerms": [KEYWORD],
    "maxResultsPerSearch": MAX_PRODUCTS,
    "maxMoq": ORDER_QTY,      # filtered by Global Sources itself, so dropped products are not charged
    "includeAds": False,
})
products = list(client.dataset(run["defaultDatasetId"]).iterate_items())

FIELDS = ["title", "priceMin", "priceMax", "moq", "moqUnit", "leadTimeDays", "fobPort",
          "supplierName", "supplierLocation", "supplierLevel", "supplierYearsOnGlobalSources",
          "verifiedManufacturer", "verifiedSupplier", "url"]
with open("globalsources_products.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    w.writerows(products)

fits = [p for p in products if p.get("moq") is None or p["moq"] <= ORDER_QTY]
priced = [p["priceMin"] for p in fits if p.get("priceMin")]
factories = sum(1 for p in fits if p.get("verifiedManufacturer"))
print(f'"{KEYWORD}": {len(products)} products, {len(fits)} with MOQ <= {ORDER_QTY}, '
      f"{factories} from verified manufacturers")
if priced:
    priced.sort()
    print(f"FOB 'from' price: min ${priced[0]:.2f}, median ${priced[len(priced) // 2]:.2f}, max ${priced[-1]:.2f}")

suppliers = defaultdict(lambda: {"products": 0, "cheapest": None})
for p in fits:
    s = suppliers[p["supplierName"]]
    s["products"] += 1
    s.update(level=p.get("supplierLevel"), years=p.get("supplierYearsOnGlobalSources"),
             factory=bool(p.get("verifiedManufacturer")), url=p.get("supplierUrl"))
    if p.get("priceMin") and (s["cheapest"] is None or p["priceMin"] < s["cheapest"]):
        s["cheapest"], s["moq"], s["unit"] = p["priceMin"], p.get("moq"), p.get("moqUnit")

ranked = sorted(suppliers.items(), key=lambda kv: (not kv[1]["factory"], -(kv[1]["level"] or 0), -(kv[1]["years"] or 0)))
print(f"\n{'factory':<8}{'rank':<6}{'years':<7}{'from $':<9}{'MOQ':<14}supplier")
for name, s in ranked[:15]:
    price = f"{s['cheapest']:.2f}" if s["cheapest"] else "hidden"
    moq = f"{s.get('moq')} {(s.get('unit') or '').lower()}" if s["cheapest"] else "-"
    print(f"{'yes' if s['factory'] else 'no':<8}{'P' + str(s['level']):<6}{s['years'] or '?':<7}{price:<9}{moq:<14}{name}")
