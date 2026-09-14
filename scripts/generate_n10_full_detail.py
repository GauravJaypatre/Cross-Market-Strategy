"""Generate results/full_battery/n10_full_detail.csv for the 50 qualifying n>=10 pairs.

Computes all 5 tracks per pair (50 pairs x 5 tracks = 250 rows),
including bootstrap CI low/high for each track.
"""

import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Dict, Any, List
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import load_universe
from src.data.loader import load_index_data
from src.parser.battery_specs import CANONICAL_BATTERY
from src.parser.llm_parser import StrategyParser
from src.tax.tax_calculator import TaxCalculator, apply_tax_adjustment
from src.brokerage.brokerage_calculator import BrokerageCalculator, apply_brokerage_adjustment
from src.engine.backtest import run_backtest_simulation, run_buy_and_hold_benchmark


def slugify(text: str) -> str:
    import re
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", s)


def compute_trade_bootstrap_ci(trades, total_years, seed=42, n_boot=1000):
    """Compute 1000-sample bootstrap 95% CI on CAGR from a list of trades."""
    if len(trades) < 2:
        return None, None
    
    # Calculate realized percentage return for each trade
    trade_returns = []
    for t in trades:
        cost = t.entry_price * t.shares
        if cost > 0:
            ret = t.net_pnl / cost if hasattr(t, 'net_pnl') and t.net_pnl != 0.0 else t.gross_return_pct
        else:
            ret = t.gross_return_pct
        trade_returns.append(ret)
        
    trade_returns = np.array(trade_returns)
    rng = np.random.default_rng(seed)
    boot_cagrs = []
    
    for _ in range(n_boot):
        boot_sample = rng.choice(trade_returns, size=len(trade_returns), replace=True)
        final_mult = float(np.prod(1.0 + boot_sample))
        if final_mult > 0 and total_years > 0:
            boot_cagrs.append(final_mult ** (1.0 / total_years) - 1.0)
        else:
            boot_cagrs.append(-1.0)
            
    ci_low = float(np.percentile(boot_cagrs, 2.5))
    ci_high = float(np.percentile(boot_cagrs, 97.5))
    return round(ci_low, 6), round(ci_high, 6)


def main():
    universe_path = "universe.yaml"
    tax_path = "tax_dataset.csv"
    brokerage_path = "brokerage_dataset.csv"
    data_dir = Path("data")
    out_dir = Path("results/full_battery")
    out_csv = out_dir / "n10_full_detail.csv"

    # Identify the 50 qualifying pairs from robustness_summary.csv
    df_rob = pd.read_csv(out_dir / "robustness_summary.csv")
    n10_pairs = df_rob[(df_rob["n_trades_is"] >= 10) & (df_rob["n_trades_oos"] >= 10)]
    n10_keys = set(zip(n10_pairs["strategy"], n10_pairs["country"], n10_pairs["index"]))
    print(f"Identified {len(n10_keys)} qualifying pairs.")

    universe_items = {u.data_source_id: u for u in load_universe(universe_path)}
    universe_list = load_universe(universe_path)
    item_by_country_index = {(u.country, u.index_name): u for u in universe_list}
    
    tax_calc = TaxCalculator(tax_path)
    broker_calc = BrokerageCalculator(brokerage_path)
    
    # Preload market data
    cached_data = {}
    for u in universe_list:
        df, prov = load_index_data(u.data_source_id, u.country, u.index_name, data_dir=data_dir)
        cached_data[u.data_source_id] = (df, prov)
        
    rule_parser = StrategyParser(backend="rule_based")
    
    # Target only strategies present in n10_keys: S2 (14-Day RSI) and S5 (Bollinger Bands)
    target_strats = [s for s in CANONICAL_BATTERY if s.name in {"14-Day RSI Oscillator", "Bollinger Bands Breakout"}]
    
    rows = []
    
    for strat in target_strats:
        parsed_strat, _ = rule_parser.parse(strat.strategy_text)
        local_env = {}
        exec(parsed_strat.generated_code, {"pd": pd, "np": np}, local_env)
        gen_signals = local_env["generate_signals"]
        
        for u in universe_list:
            if (strat.name, u.country, u.index_name) not in n10_keys:
                continue
                
            df, prov = cached_data[u.data_source_id]
            signals = gen_signals(df)
            
            c_days = max(1, (df.index[-1] - df.index[0]).days)
            total_years = c_days / 365.25
            
            # Salted seed per pair
            pair_salt = int(hashlib.sha256(f"{strat.id}_{u.country}_{u.index_name}_42".encode()).hexdigest()[:8], 16)
            seed_base = (42 + pair_salt) % (2**31 - 1)
            
            # 1. Gross Track
            raw_trades, gross_curve, gross_m = run_backtest_simulation(df, signals, initial_capital=100000.0)
            ci_l_gross, ci_h_gross = compute_trade_bootstrap_ci(raw_trades, total_years, seed=seed_base)
            
            # 2. Net-Tax Track
            tax_trades, tax_curve, tax_m = apply_tax_adjustment(raw_trades, gross_curve, u.country, tax_calc, initial_capital=100000.0)
            ci_l_tax, ci_h_tax = compute_trade_bootstrap_ci(tax_trades, total_years, seed=seed_base + 1)
            
            # 3. Net-Discount Track
            disc_trades, disc_curve, disc_m = apply_brokerage_adjustment(tax_trades, tax_curve, u.country, "discount", broker_calc)
            ci_l_disc, ci_h_disc = compute_trade_bootstrap_ci(disc_trades, total_years, seed=seed_base + 2)
            
            # 4. Net-Full-Service Track
            fs_trades, fs_curve, fs_m = apply_brokerage_adjustment(tax_trades, tax_curve, u.country, "full_service", broker_calc)
            ci_l_fs, ci_h_fs = compute_trade_bootstrap_ci(fs_trades, total_years, seed=seed_base + 3)
            
            # 5. Buy-and-Hold Track
            bh_trades, bh_raw_curve, _ = run_buy_and_hold_benchmark(df, initial_capital=100000.0)
            bh_tax_trades, bh_tax_curve, _ = apply_tax_adjustment(bh_trades, bh_raw_curve, u.country, tax_calc, initial_capital=100000.0)
            bh_disc_trades, bh_disc_curve, bh_m = apply_brokerage_adjustment(bh_tax_trades, bh_tax_curve, u.country, "discount", broker_calc)
            # For 1 trade, CI low/high is the point estimate
            ci_l_bh = round(bh_m.cagr, 6)
            ci_h_bh = round(bh_m.cagr, 6)
            
            tracks_data = [
                ("Gross", gross_m, ci_l_gross, ci_h_gross),
                ("Net-Tax", tax_m, ci_l_tax, ci_h_tax),
                ("Net-Discount", disc_m, ci_l_disc, ci_h_disc),
                ("Net-Full-Service", fs_m, ci_l_fs, ci_h_fs),
                ("Buy-and-Hold", bh_m, ci_l_bh, ci_h_bh),
            ]
            
            for trk_name, m, ci_l, ci_h in tracks_data:
                rows.append({
                    "strategy": strat.name,
                    "country": u.country,
                    "index": u.index_name,
                    "track": trk_name,
                    "CAGR": round(m.cagr, 6),
                    "MaxDD": round(m.max_drawdown, 6),
                    "Calmar": round(m.calmar_ratio, 6),
                    "Sharpe": round(m.sharpe_ratio, 6),
                    "n_trades": m.total_trades,
                    "bootstrap_ci_low": ci_l if ci_l is not None else "N/A",
                    "bootstrap_ci_high": ci_h if ci_h is not None else "N/A",
                })
                
    fieldnames = [
        "strategy",
        "country",
        "index",
        "track",
        "CAGR",
        "MaxDD",
        "Calmar",
        "Sharpe",
        "n_trades",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
    ]
    
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Saved {len(rows)} rows to {out_csv}")
    
    # Active vs passive count check
    df_res = pd.DataFrame(rows)
    loses_to_bh = 0
    for strat in target_strats:
        for u in universe_list:
            if (strat.name, u.country, u.index_name) not in n10_keys:
                continue
            d_cagr = df_res[(df_res['strategy']==strat.name) & (df_res['index']==u.index_name) & (df_res['track']=='Net-Discount')]['CAGR'].iloc[0]
            b_cagr = df_res[(df_res['strategy']==strat.name) & (df_res['index']==u.index_name) & (df_res['track']=='Buy-and-Hold')]['CAGR'].iloc[0]
            if d_cagr < b_cagr:
                loses_to_bh += 1
                
    pct_loses = (loses_to_bh / len(n10_keys)) * 100
    print(f"COUNT_ACTIVE_LOSES_TO_PASSIVE: {loses_to_bh} of {len(n10_keys)} ({pct_loses:.2f}%)")


if __name__ == "__main__":
    main()
