import csv
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import load_universe
from src.data.loader import load_index_data
from src.parser.battery_specs import CANONICAL_BATTERY
from src.parser.llm_parser import StrategyParser
from src.tax.tax_calculator import TaxCalculator
from src.brokerage.brokerage_calculator import BrokerageCalculator
from src.multi_track.track_simulator import run_multi_track_simulation

# Temporary CSVs for old parameters
old_tax_csv = "scratch/old_tax.csv"
old_broker_csv = "scratch/old_broker.csv"

# Read current tax and brokerage
df_tax = pd.read_csv("tax_dataset.csv")
df_tax_old = df_tax[df_tax["country"] != "Japan"].copy()
japan_old = pd.DataFrame([{
    "country": "Japan",
    "tax_regime_name": "Shotokuzei + Local + Fukkou 2011-2025",
    "rate_type": "flat",
    "rate_pct": 20.315,
    "holding_period_threshold_days": 0,
    "rate_short_pct": 0.0,
    "rate_long_pct": 0.0,
    "exemption_threshold_local_currency": 0,
    "effective_from": "2011-01-01",
    "effective_to": "2025-12-31",
    "source_url": "https://www.nta.go.jp",
    "source_type": "statute",
    "confidence": "primary_statutory_single_source",
    "notes": "15 pct national + 5 pct local + 0.315 pct reconstruction special tax"
}])
df_tax_old = pd.concat([df_tax_old, japan_old], ignore_index=True)
df_tax_old.to_csv(old_tax_csv, index=False)

df_broker = pd.read_csv("brokerage_dataset.csv")
df_broker_old = df_broker[~((df_broker["country"] == "Germany") & (df_broker["broker_type"] == "discount"))].copy()
germany_old = pd.DataFrame([{
    "country": "Germany",
    "broker_name": "Trade Republic",
    "broker_type": "discount",
    "fee_model": "flat_per_trade",
    "flat_fee_local_currency": 1.0,
    "pct_fee": 0.0,
    "min_fee_local_currency": 0.0,
    "max_fee_local_currency": 0.0,
    "fee_tax_rate_pct": 0.0,
    "other_charges_pct": 0.0,
    "effective_from": "2011-01-01",
    "effective_to": "2025-12-31",
    "source_url": "https://traderepublic.com",
    "confidence": "primary_statutory_single_source",
    "selection_criterion": "Representative neo-broker flat fee",
    "selection_basis_date": "2024-01-01"
}])
df_broker_old = pd.concat([df_broker_old, germany_old], ignore_index=True)
df_broker_old.to_csv(old_broker_csv, index=False)

tax_calc_old = TaxCalculator(old_tax_csv)
broker_calc_old = BrokerageCalculator(old_broker_csv)

all_universe = load_universe("universe.yaml")
affected_universe = [u for u in all_universe if u.country in {"Japan", "Germany"}]

rule_parser = StrategyParser(backend="rule_based")
compiled = []
for strat in CANONICAL_BATTERY:
    parsed, _ = rule_parser.parse(strat.strategy_text)
    local_env = {}
    exec(parsed.generated_code, {"pd": pd, "np": np}, local_env)
    compiled.append((strat, local_env["generate_signals"]))

df_new_rob = pd.read_csv("results/full_battery/robustness_summary.csv")
new_rob_map = {(r['strategy'], r['country'], r['index']): r for _, r in df_new_rob.iterrows() if r['country'] in ['Japan', 'Germany']}

rob_deltas = []
for strat, gen_signals in compiled:
    for u in affected_universe:
        df, prov = load_index_data(u.data_source_id, u.country, u.index_name, data_dir=Path("data"))
        signals = gen_signals(df)
        res_old = run_multi_track_simulation(
            df=df,
            signals=signals,
            country=u.country,
            index_name=u.index_name,
            data_source_id=u.data_source_id,
            currency=u.currency,
            provenance=prov,
            tax_calculator=tax_calc_old,
            brokerage_calculator=broker_calc_old,
            initial_capital=100000.0,
            risk_free_rate=0.0,
            seed=42,
        )
        ro = res_old.robustness
        rn = new_rob_map.get((strat.name, u.country, u.index_name))

        diffs = {}
        metrics = [
            ("is_cagr", ro.is_cagr, rn["is_cagr"]),
            ("oos_cagr", ro.oos_cagr, rn["oos_cagr"]),
            ("mc_p95_maxdd", ro.mc_p95_max_drawdown, rn["mc_p95_maxdd"]),
            ("bootstrap_ci_low", ro.cagr_ci_lower, rn["bootstrap_ci_low"]),
            ("bootstrap_ci_high", ro.cagr_ci_upper, rn["bootstrap_ci_high"]),
        ]
        for name, vo, vn in metrics:
            if abs(round(float(vo), 6) - round(float(vn), 6)) > 1e-6:
                diffs[name] = (round(float(vo), 6), round(float(vn), 6))

        is_trades = ro.is_trade_count
        oos_trades = ro.oos_trade_count
        guard = (is_trades < 3) or (oos_trades < 2)
        deg_o = round(float(ro.degradation_ratio), 6) if not guard else "N/A"
        deg_n = rn["degradation_ratio"]
        if str(deg_o) != str(deg_n):
            if deg_o != "N/A" and deg_n != "N/A":
                if abs(float(deg_o) - float(deg_n)) > 1e-6:
                    diffs["degradation_ratio"] = (deg_o, deg_n)
            else:
                diffs["degradation_ratio"] = (deg_o, deg_n)

        if diffs:
            rob_deltas.append(((strat.name, u.country, u.index_name), diffs))

print(f"Total pairs with robustness changes: {len(rob_deltas)}")
for (strat, country, idx), diffs in rob_deltas:
    print(f"\n[{strat} | {country} - {idx}]")
    for m, (vo, vn) in diffs.items():
        delta = vn - vo if isinstance(vo, (int, float)) and isinstance(vn, (int, float)) else "N/A"
        print(f"  {m}: {vo} -> {vn} (delta: {delta:+f})")
