import pandas as pd
import numpy as np

df_rob = pd.read_csv("results/full_battery/robustness_summary.csv")
df_sum = pd.read_csv("results/full_battery/summary_cross_country.csv")

targets = [
    ("50/200 SMA Crossover", "United States", "Nasdaq Composite"),
    ("12-Month Momentum (Monthly Rebalance)", "United States", "Nasdaq Composite"),
    ("52-Week High Drawdown Dip Buyer", "Japan", "Nikkei 225"),
    ("52-Week High Drawdown Dip Buyer", "United States", "Nasdaq Composite"),
]

print("=== PART 1: 4 LEADERBOARD WINNING PAIRS ===")
for s, c, i in targets:
    r_row = df_rob[(df_rob["strategy"] == s) & (df_rob["country"] == c) & (df_rob["index"] == i)]
    s_rows = df_sum[(df_sum["strategy"] == s) & (df_sum["country"] == c) & (df_sum["index"] == i)]
    print(f"\nTarget: {s} | {c} - {i}")
    if not r_row.empty:
        r = r_row.iloc[0]
        ci_w = r["bootstrap_ci_high"] - r["bootstrap_ci_low"]
        print(f"  Robustness Summary (Net-Discount):")
        print(f"    IS_CAGR: {r['is_cagr']}")
        print(f"    OOS_CAGR: {r['oos_cagr']}")
        print(f"    bootstrap_ci_low: {r['bootstrap_ci_low']}")
        print(f"    bootstrap_ci_high: {r['bootstrap_ci_high']}")
        print(f"    CI_width: {ci_w:.6f}")
        print(f"    n_trades_is: {r['n_trades_is']}")
        print(f"    n_trades_oos: {r['n_trades_oos']}")

    print("  All Tracks (Point-Estimate CAGR from summary_cross_country.csv):")
    for _, sr in s_rows.iterrows():
        print(f"    Track: {sr['track']:<18} | CAGR: {sr['CAGR']:.6f} | MaxDD: {sr['MaxDD']:.6f} | Calmar: {sr['Calmar']:.6f} | Trades: {sr['n_trades']}")

# Correlation
min_trades = np.minimum(df_rob["n_trades_is"], df_rob["n_trades_oos"])
ci_width = df_rob["bootstrap_ci_high"] - df_rob["bootstrap_ci_low"]
df_rob["min_trades"] = min_trades
df_rob["ci_width"] = ci_width

corr_pearson = np.corrcoef(min_trades, ci_width)[0, 1]
corr_spearman = df_rob[["min_trades", "ci_width"]].corr(method="spearman").iloc[0, 1]

print("\n=== CORRELATION ANALYSIS ===")
print(f"Pearson correlation (min(n_trades_is, n_trades_oos) vs CI_width): {corr_pearson:.6f}")
print(f"Spearman correlation (min(n_trades_is, n_trades_oos) vs CI_width): {corr_spearman:.6f}")

# Part 2: n >= 10 qualification
n10_pairs = df_rob[(df_rob["n_trades_is"] >= 10) & (df_rob["n_trades_oos"] >= 10)]
print("\n=== PART 2: LEADERBOARD N10 THRESHOLD ===")
print(f"Pairs with n_trades_is >= 10 AND n_trades_oos >= 10: {len(n10_pairs)} of 150")
print("Breakdown by strategy:")
for strat, cnt in n10_pairs["strategy"].value_counts().items():
    print(f"  {strat}: {cnt}")
