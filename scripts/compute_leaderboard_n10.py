import pandas as pd
import csv
from pathlib import Path

df_rob = pd.read_csv("results/full_battery/robustness_summary.csv")
df_sum = pd.read_csv("results/full_battery/summary_cross_country.csv")

# Filter df_rob to n_trades_is >= 10 and n_trades_oos >= 10
qualified_n10 = df_rob[(df_rob["n_trades_is"] >= 10) & (df_rob["n_trades_oos"] >= 10)]
qualified_keys = set(zip(qualified_n10["strategy"], qualified_n10["country"], qualified_n10["index"]))

print(f"Total qualified (strategy, country, index) triplets: {len(qualified_keys)}")

tracks_order = ["Gross", "Net-Tax", "Net-Discount", "Net-Full-Service", "Buy-and-Hold"]
all_strategies = df_sum["strategy"].unique().tolist()

rows_full = []
rows_only_qual = []

for strat_name in all_strategies:
    for trk in tracks_order:
        sub = df_sum[(df_sum["strategy"] == strat_name) & (df_sum["track"] == trk)]
        # filter to only those in qualified_keys
        qual_sub = sub[sub.apply(lambda r: (r["strategy"], r["country"], r["index"]) in qualified_keys, axis=1)]
        
        if not qual_sub.empty:
            best_cagr_row = qual_sub.loc[qual_sub["CAGR"].idxmax()]
            best_cagr_str = f"{best_cagr_row['country']} - {best_cagr_row['index']}"
            best_cagr_val = best_cagr_row["CAGR"]

            best_calmar_row = qual_sub.loc[qual_sub["Calmar"].idxmax()]
            best_calmar_str = f"{best_calmar_row['country']} - {best_calmar_row['index']}"
            best_calmar_val = best_calmar_row["Calmar"]

            row_data = {
                "strategy": strat_name,
                "track": trk,
                "best_by_cagr_index": best_cagr_str,
                "cagr": round(float(best_cagr_val), 6),
                "best_by_calmar_index": best_calmar_str,
                "calmar": round(float(best_calmar_val), 6),
            }
            rows_only_qual.append(row_data)
            rows_full.append(row_data)
        else:
            row_data = {
                "strategy": strat_name,
                "track": trk,
                "best_by_cagr_index": "N/A (0 pairs qualify n>=10)",
                "cagr": "N/A",
                "best_by_calmar_index": "N/A (0 pairs qualify n>=10)",
                "calmar": "N/A",
            }
            rows_full.append(row_data)

out_csv_path = Path("results/full_battery/leaderboard_n10.csv")
with open(out_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["strategy", "track", "best_by_cagr_index", "cagr", "best_by_calmar_index", "calmar"])
    writer.writeheader()
    writer.writerows(rows_full)

print(f"Saved {len(rows_full)} rows to {out_csv_path}")
print("\n--- Qualifying Rows Only (10 rows) ---")
df_qual_only = pd.DataFrame(rows_only_qual)
print(df_qual_only.to_string(index=False))

print("\n--- Full 30 Rows Table ---")
df_full = pd.DataFrame(rows_full)
print(df_full.to_string(index=False))
