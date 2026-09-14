"""Compute Benjamini-Hochberg FDR correction on the n>=10 subset.

From results/full_battery/n10_full_detail.csv (50 pairs, Net-Discount track),
for each pair compute a one-sided test of whether Net-Discount CAGR exceeds
Buy-and-Hold CAGR, using the existing bootstrap distribution (1000 resamples):
the p-value is the proportion of bootstrap CAGR draws that fall at or below
the Buy-and-Hold CAGR for that same pair.

Apply Benjamini-Hochberg FDR correction (q = 0.10) across all 50 p-values jointly.
Outputs results/full_battery/fdr_corrected_significance.csv.
"""

import csv
import hashlib
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smm

# Add repo root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.config import load_universe
from src.data.loader import load_index_data
from src.parser.battery_specs import CANONICAL_BATTERY
from src.parser.llm_parser import StrategyParser
from src.tax.tax_calculator import TaxCalculator, apply_tax_adjustment
from src.brokerage.brokerage_calculator import BrokerageCalculator, apply_brokerage_adjustment
from src.engine.backtest import run_backtest_simulation, run_buy_and_hold_benchmark


def main():
    repo_root = Path(__file__).resolve().parent.parent
    universe_path = repo_root / "universe.yaml"
    tax_path = repo_root / "tax_dataset.csv"
    brokerage_path = repo_root / "brokerage_dataset.csv"
    data_dir = repo_root / "data"
    n10_detail_path = repo_root / "results" / "full_battery" / "n10_full_detail.csv"
    out_csv = repo_root / "results" / "full_battery" / "fdr_corrected_significance.csv"

    # Read n10_full_detail.csv
    df_n10 = pd.read_csv(n10_detail_path)
    disc_df = df_n10[df_n10["track"] == "Net-Discount"].copy()
    bh_df = df_n10[df_n10["track"] == "Buy-and-Hold"].copy()

    universe_list = load_universe(universe_path)
    tax_calc = TaxCalculator(tax_path)
    broker_calc = BrokerageCalculator(brokerage_path)

    # Preload market data
    cached_data = {}
    for u in universe_list:
        df, prov = load_index_data(u.data_source_id, u.country, u.index_name, data_dir=data_dir)
        cached_data[u.data_source_id] = (df, prov)

    rule_parser = StrategyParser(backend="rule_based")
    target_strats = [s for s in CANONICAL_BATTERY if s.name in {"14-Day RSI Oscillator", "Bollinger Bands Breakout"}]

    records = []

    # Preserve order of the 50 pairs from disc_df
    for _, row in disc_df.iterrows():
        strat_name = row["strategy"]
        ctry = row["country"]
        idx = row["index"]
        cagr_disc = float(row["CAGR"])

        # Buy-and-Hold benchmark
        bh_row = bh_df[(bh_df["strategy"] == strat_name) & (bh_df["country"] == ctry) & (bh_df["index"] == idx)].iloc[0]
        cagr_bh = float(bh_row["CAGR"])
        diff_pp = (cagr_disc - cagr_bh) * 100.0

        # Find strategy object & universe item
        strat_obj = next(s for s in target_strats if s.name == strat_name)
        u_obj = next(u for u in universe_list if u.country == ctry and u.index_name == idx)

        parsed_strat, _ = rule_parser.parse(strat_obj.strategy_text)
        local_env = {}
        exec(parsed_strat.generated_code, {"pd": pd, "np": np}, local_env)
        gen_signals = local_env["generate_signals"]

        df, prov = cached_data[u_obj.data_source_id]
        signals = gen_signals(df)
        c_days = max(1, (df.index[-1] - df.index[0]).days)
        total_years = c_days / 365.25

        # Salted seed matching canonical battery & generate_n10_full_detail.py
        pair_salt = int(hashlib.sha256(f"{strat_obj.id}_{u_obj.country}_{u_obj.index_name}_42".encode()).hexdigest()[:8], 16)
        seed_base = (42 + pair_salt) % (2**31 - 1)

        raw_trades, gross_curve, _ = run_backtest_simulation(df, signals, initial_capital=100000.0)
        tax_trades, tax_curve, _ = apply_tax_adjustment(raw_trades, gross_curve, u_obj.country, tax_calc, initial_capital=100000.0)
        disc_trades, disc_curve, disc_m = apply_brokerage_adjustment(tax_trades, tax_curve, u_obj.country, "discount", broker_calc)

        trade_returns = []
        for t in disc_trades:
            cost = t.entry_price * t.shares
            if cost > 0:
                ret = t.net_pnl / cost if hasattr(t, "net_pnl") and t.net_pnl != 0.0 else t.gross_return_pct
            else:
                ret = t.gross_return_pct
            trade_returns.append(ret)

        trade_returns = np.array(trade_returns)
        rng = np.random.default_rng(seed_base + 2)
        boot_cagrs = []
        for _ in range(1000):
            boot_sample = rng.choice(trade_returns, size=len(trade_returns), replace=True)
            final_mult = float(np.prod(1.0 + boot_sample))
            if final_mult > 0 and total_years > 0:
                boot_cagrs.append(final_mult ** (1.0 / total_years) - 1.0)
            else:
                boot_cagrs.append(-1.0)

        boot_cagrs = np.array(boot_cagrs)

        # Proportion of bootstrap CAGR draws that fall at or below Buy-and-Hold CAGR
        raw_p = float(np.mean(boot_cagrs <= cagr_bh))

        records.append({
            "strategy": strat_name,
            "country": ctry,
            "index": idx,
            "cagr_disc": cagr_disc,
            "cagr_bh": cagr_bh,
            "raw_cagr_outperformance_pp": diff_pp,
            "raw_p_value": raw_p,
        })

    # Apply Benjamini-Hochberg FDR correction (q = 0.10) across all 50 p-values jointly
    raw_p_vals = [r["raw_p_value"] for r in records]
    reject, p_adjusted, _, _ = smm.multipletests(raw_p_vals, alpha=0.10, method="fdr_bh")

    for i, r in enumerate(records):
        r["bh_adjusted_p_value"] = float(p_adjusted[i])
        r["significant_at_q10"] = bool(reject[i])

    # Write results to CSV
    fieldnames = [
        "strategy",
        "country",
        "index",
        "raw_cagr_outperformance_pp",
        "raw_p_value",
        "bh_adjusted_p_value",
        "significant_at_q10",
    ]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                "strategy": r["strategy"],
                "country": r["country"],
                "index": r["index"],
                "raw_cagr_outperformance_pp": round(r["raw_cagr_outperformance_pp"], 4),
                "raw_p_value": round(r["raw_p_value"], 4),
                "bh_adjusted_p_value": round(r["bh_adjusted_p_value"], 4),
                "significant_at_q10": r["significant_at_q10"],
            })

    print(f"Successfully written {len(records)} rows to results/full_battery/fdr_corrected_significance.csv")

    # Check the 4 previously identified outperformers
    print("\n=== 4 PREVIOUSLY-IDENTIFIED OUTPERFORMERS ===")
    target_pairs = [
        ("14-Day RSI Oscillator", "United Kingdom", "FTSE 100"),
        ("14-Day RSI Oscillator", "Italy", "FTSE MIB"),
        ("Bollinger Bands Breakout", "China", "Shenzhen Component"),
        ("Bollinger Bands Breakout", "China", "Shanghai Composite"),
    ]
    for s, c, i in target_pairs:
        match = next(r for r in records if r["strategy"] == s and r["country"] == c and r["index"] == i)
        print(f"{s} | {c} - {i}:")
        print(f"  Raw Outperformance: {match['raw_cagr_outperformance_pp']:+.4f} pp")
        print(f"  Raw p-value:        {match['raw_p_value']:.4f}")
        print(f"  BH-adjusted p-value:{match['bh_adjusted_p_value']:.4f}")
        print(f"  Significant at q=0.10: {match['significant_at_q10']}")
        print(f"  Survives FDR: {'YES' if match['significant_at_q10'] else 'NO'}\n")


if __name__ == "__main__":
    main()
