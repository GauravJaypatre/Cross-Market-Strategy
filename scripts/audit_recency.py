import csv
import sys
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

tax_by_country = defaultdict(list)
with open("tax_dataset.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        tax_by_country[row["country"]].append(row)

broker_by_country = defaultdict(list)
with open("brokerage_dataset.csv", "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        broker_by_country[row["country"]].append(row)

all_countries = sorted(set(tax_by_country.keys()) | set(broker_by_country.keys()))

print(f"{'Country':15} | {'Tax Max From':12} | {'Broker Max From':15} | {'Needs Audit?'}")
print("-" * 75)

needs_audit = []
for c in all_countries:
    t_rows = tax_by_country.get(c, [])
    b_rows = broker_by_country.get(c, [])

    t_max_from = max([r["effective_from"] for r in t_rows]) if t_rows else "N/A"
    b_max_from = max([r["effective_from"] for r in b_rows]) if b_rows else "N/A"

    # Criteria: has no rate-change event dated after 2022-12-31
    tax_stale = t_max_from <= "2022-12-31"
    broker_stale = b_max_from <= "2022-12-31"

    flag = ""
    if tax_stale and broker_stale:
        flag = "Both Tax & Broker <= 2022"
    elif tax_stale:
        flag = "Tax <= 2022"
    elif broker_stale:
        flag = "Broker <= 2022"
    else:
        flag = "Both have post-2022 events"

    print(f"{c:15} | {t_max_from:12} | {b_max_from:15} | {flag}")
    if tax_stale or broker_stale:
        needs_audit.append((c, t_max_from, b_max_from, flag))

print("\n=== Detailed rows for countries with events <= 2022-12-31 ===")
for c, t_max, b_max, flag in needs_audit:
    print(f"\n--- {c} ({flag}) ---")
    print("Tax Regimes:")
    for r in tax_by_country.get(c, []):
        print(f"  {r['effective_from']} to {r['effective_to']}: {r['tax_regime_name']} -> {r['rate_type']} (rate_pct={r['rate_pct']}, short={r['rate_short_pct']}, long={r['rate_long_pct']})")
    print("Broker Schedules:")
    for r in broker_by_country.get(c, []):
        print(f"  {r['effective_from']} to {r['effective_to']} [{r['broker_type']} - {r['broker_name']}]: fee_model={r['fee_model']}, flat={r['flat_fee_local_currency']}, pct={r['pct_fee']}, other={r['other_charges_pct']}")
