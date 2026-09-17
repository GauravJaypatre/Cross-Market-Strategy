"""Script to re-run only the 6 France CAC 40 pairs after France FTT rate update (0.4% effective 2025-04-01).

Updates:
- results/full_battery/{strat_slug}/france_cac_40/
- results/full_battery/summary_cross_country.csv
- results/full_battery/robustness_summary.csv
- results/full_battery/leaderboard.csv
- results/full_battery/leaderboard_n10.csv
- results/full_battery/n10_full_detail.csv
- results/full_battery/fdr_corrected_significance.csv

Logs all deltas: old vs corrected value.
"""

import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import statsmodels.stats.multitest as smm

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import load_universe
from src.data.loader import load_index_data
from src.parser.battery_specs import CANONICAL_BATTERY
from src.parser.llm_parser import StrategyParser
from src.tax.tax_calculator import TaxCalculator, apply_tax_adjustment
from src.brokerage.brokerage_calculator import BrokerageCalculator, apply_brokerage_adjustment
from src.multi_track.track_simulator import run_multi_track_simulation
from src.reporting.reporter import generate_reports
from src.engine.backtest import run_backtest_simulation, run_buy_and_hold_benchmark


def slugify(text: str) -> str:
    import re
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", s)


def compute_trade_bootstrap_ci(trades, total_years, seed=42, n_boot=1000):
    """Compute 1000-sample bootstrap 95% CI on CAGR from a list of trades."""
    if len(trades) < 2:
        return None, None
    
    trade_returns = []
    for t in trades:
        cost = t.entry_price * t.shares
        if cost > 0:
            ret = t.net_pnl / cost if hasattr(t, "net_pnl") and t.net_pnl != 0.0 else t.gross_return_pct
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
            
    sorted_cagrs = np.sort(boot_cagrs)
    ci_lower = float(np.percentile(sorted_cagrs, 2.5))
    ci_upper = float(np.percentile(sorted_cagrs, 97.5))
    return round(ci_lower, 6), round(ci_upper, 6)


def main():
    repo_root = Path(__file__).resolve().parent.parent
    base_dir = repo_root / "results" / "full_battery"
    universe_path = repo_root / "universe.yaml"
    tax_path = repo_root / "tax_dataset.csv"
    brokerage_path = repo_root / "brokerage_dataset.csv"
    data_dir = repo_root / "data"

    # 1. Load universe, find France index
    all_universe = load_universe(universe_path)
    france_universe = [u for u in all_universe if u.country == "France"]
    print(f"France indices ({len(france_universe)}): {[f'{u.country} - {u.index_name}' for u in france_universe]}")

    tax_calc = TaxCalculator(tax_path)
    broker_calc = BrokerageCalculator(brokerage_path)

    # Pre-load market data for France
    cached_market_data = {}
    for u in france_universe:
        df, prov = load_index_data(u.data_source_id, u.country, u.index_name, data_dir=data_dir)
        cached_market_data[u.data_source_id] = (df, prov)

    rule_parser = StrategyParser(backend="rule_based")
    compiled_strategies = []
    for strat in CANONICAL_BATTERY:
        parsed_strat, audit_rec = rule_parser.parse(strat.strategy_text)
        local_env = {}
        exec(parsed_strat.generated_code, {"pd": pd, "np": np}, local_env)
        compiled_strategies.append({
            "spec": strat,
            "audit": audit_rec,
            "generate_signals": local_env["generate_signals"],
            "slug": slugify(f"{strat.id}_{strat.name}"),
        })

    # Read existing summary files to capture old values
    df_old_summary = pd.read_csv(base_dir / "summary_cross_country.csv")
    df_old_rob = pd.read_csv(base_dir / "robustness_summary.csv")
    df_old_lead = pd.read_csv(base_dir / "leaderboard.csv")
    df_old_lead_n10 = pd.read_csv(base_dir / "leaderboard_n10.csv")

    deltas_cagr = []
    new_summary_rows = []
    new_rob_rows = []

    for strat_info in compiled_strategies:
        strat = strat_info["spec"]
        strat_slug = strat_info["slug"]
        strat_dir = base_dir / strat_slug

        for u in france_universe:
            df, prov = cached_market_data[u.data_source_id]
            signals = strat_info["generate_signals"](df)

            res = run_multi_track_simulation(
                df=df,
                signals=signals,
                country=u.country,
                index_name=u.index_name,
                data_source_id=u.data_source_id,
                currency=u.currency,
                provenance=prov,
                tax_calculator=tax_calc,
                brokerage_calculator=broker_calc,
                initial_capital=100000.0,
                risk_free_rate=0.0,
                seed=42,
            )

            pair_slug = slugify(f"{u.country}_{u.index_name}")
            pair_dir = strat_dir / pair_slug
            pair_dir.mkdir(parents=True, exist_ok=True)
            generate_reports(
                results=[res],
                audit_record=strat_info["audit"],
                output_dir=pair_dir,
                seed=42,
            )

            # Compare old vs new in summary_cross_country
            tracks_info = [
                ("Gross", res.gross_metrics),
                ("Net-Tax", res.net_tax_metrics),
                ("Net-Discount", res.net_discount_metrics),
                ("Net-Full-Service", res.net_full_service_metrics),
                ("Buy-and-Hold", res.benchmark_discount_metrics),
            ]

            is_qualified = (res.exclusion_reason is None)

            for trk_name, m in tracks_info:
                old_row = df_old_summary[
                    (df_old_summary["strategy"] == strat.name)
                    & (df_old_summary["country"] == u.country)
                    & (df_old_summary["index"] == u.index_name)
                    & (df_old_summary["track"] == trk_name)
                ]
                old_cagr = old_row["CAGR"].iloc[0] if not old_row.empty else None
                old_maxdd = old_row["MaxDD"].iloc[0] if not old_row.empty else None
                old_calmar = old_row["Calmar"].iloc[0] if not old_row.empty else None

                new_cagr = round(m.cagr, 6)
                new_maxdd = round(m.max_drawdown, 6)
                new_calmar = round(m.calmar_ratio, 6)

                if old_cagr is not None and (abs(old_cagr - new_cagr) > 1e-6 or abs(old_calmar - new_calmar) > 1e-6):
                    deltas_cagr.append({
                        "strategy": strat.name,
                        "country": u.country,
                        "index": u.index_name,
                        "track": trk_name,
                        "old_cagr": old_cagr,
                        "new_cagr": new_cagr,
                        "delta_cagr": round(new_cagr - old_cagr, 6),
                        "old_calmar": old_calmar,
                        "new_calmar": new_calmar,
                        "delta_calmar": round(new_calmar - old_calmar, 6),
                    })

                new_summary_rows.append({
                    "strategy": strat.name,
                    "country": u.country,
                    "index": u.index_name,
                    "track": trk_name,
                    "CAGR": new_cagr,
                    "MaxDD": new_maxdd,
                    "Calmar": new_calmar,
                    "Sharpe": round(m.sharpe_ratio, 6),
                    "n_trades": m.total_trades,
                    "qualified": is_qualified,
                })

            # Robustness row
            rob = res.robustness
            is_trades = rob.is_trade_count
            oos_trades = rob.oos_trade_count
            is_guard = rob.is_insufficient_sample or (is_trades < 3)
            oos_guard = rob.oos_insufficient_sample or (oos_trades < 2)
            guard_triggered = is_guard or oos_guard

            new_rob_rows.append({
                "strategy": strat.name,
                "country": u.country,
                "index": u.index_name,
                "track": "Net-Discount",
                "is_cagr": round(rob.is_cagr, 6),
                "oos_cagr": round(rob.oos_cagr, 6),
                "degradation_ratio": round(rob.degradation_ratio, 6) if not guard_triggered else "N/A",
                "mc_p95_maxdd": round(rob.mc_p95_max_drawdown, 6),
                "bootstrap_ci_low": round(rob.cagr_ci_lower, 6),
                "bootstrap_ci_high": round(rob.cagr_ci_upper, 6),
                "n_trades_is": is_trades,
                "n_trades_oos": oos_trades,
                "guard_triggered": guard_triggered,
            })

    print(f"\nTotal metric deltas detected across France CAC 40 pairs: {len(deltas_cagr)}")
    for d in deltas_cagr:
        print(f"  [{d['strategy']} | {d['country']} - {d['index']} | {d['track']}] CAGR: {d['old_cagr']} -> {d['new_cagr']} ({d['delta_cagr']:+f}), Calmar: {d['old_calmar']} -> {d['new_calmar']} ({d['delta_calmar']:+f})")

    # Merge into summary_cross_country.csv (replace France rows)
    df_merged_summary = df_old_summary[df_old_summary["country"] != "France"].copy()
    df_new_summary = pd.DataFrame(new_summary_rows)
    df_final_summary = pd.concat([df_merged_summary, df_new_summary], ignore_index=True)
    df_final_summary.sort_values(by=["strategy", "country", "index", "track"], inplace=True)
    df_final_summary.to_csv(base_dir / "summary_cross_country.csv", index=False)
    print(f"\nUpdated summary_cross_country.csv: {len(df_final_summary)} rows")

    # Merge into robustness_summary.csv (replace France rows)
    df_merged_rob = df_old_rob[df_old_rob["country"] != "France"].copy()
    df_new_rob = pd.DataFrame(new_rob_rows)
    df_final_rob = pd.concat([df_merged_rob, df_new_rob], ignore_index=True)
    df_final_rob.sort_values(by=["strategy", "country", "index"], inplace=True)
    df_final_rob.to_csv(base_dir / "robustness_summary.csv", index=False)
    print(f"Updated robustness_summary.csv: {len(df_final_rob)} rows")

    # Recompute leaderboard.csv
    tracks_order = ["Gross", "Net-Tax", "Net-Discount", "Net-Full-Service", "Buy-and-Hold"]
    leaderboard_rows = []
    for strat in CANONICAL_BATTERY:
        strat_name = strat.name
        for trk in tracks_order:
            sub = df_final_summary[(df_final_summary["strategy"] == strat_name) & (df_final_summary["track"] == trk)]
            qual_sub = sub[sub["qualified"] == True]
            eval_sub = qual_sub if len(qual_sub) > 0 else sub

            best_cagr_row = eval_sub.loc[eval_sub["CAGR"].idxmax()]
            best_cagr_str = f"{best_cagr_row['country']} - {best_cagr_row['index']}"
            best_cagr_val = best_cagr_row["CAGR"]

            best_calmar_row = eval_sub.loc[eval_sub["Calmar"].idxmax()]
            best_calmar_str = f"{best_calmar_row['country']} - {best_calmar_row['index']}"
            best_calmar_val = best_calmar_row["Calmar"]

            leaderboard_rows.append({
                "strategy": strat_name,
                "track": trk,
                "best_by_cagr_index": best_cagr_str,
                "cagr": round(float(best_cagr_val), 6),
                "best_by_calmar_index": best_calmar_str,
                "calmar": round(float(best_calmar_val), 6),
            })

    df_new_lead = pd.DataFrame(leaderboard_rows)
    df_new_lead.to_csv(base_dir / "leaderboard.csv", index=False)
    print(f"Updated leaderboard.csv: {len(df_new_lead)} rows")

    # Check for Leaderboard Changes
    print("\n=== LEADERBOARD DELTAS ===")
    lead_deltas = []
    for i in range(len(df_old_lead)):
        r_old = df_old_lead.iloc[i]
        r_new = df_new_lead.iloc[i]
        cagr_win_change = r_old["best_by_cagr_index"] != r_new["best_by_cagr_index"] or abs(float(r_old["cagr"]) - float(r_new["cagr"])) > 1e-6
        calmar_win_change = r_old["best_by_calmar_index"] != r_new["best_by_calmar_index"] or abs(float(r_old["calmar"]) - float(r_new["calmar"])) > 1e-6
        if cagr_win_change or calmar_win_change:
            lead_deltas.append({
                "strategy": r_new["strategy"],
                "track": r_new["track"],
                "old_best_cagr": f"{r_old['best_by_cagr_index']} ({r_old['cagr']})",
                "new_best_cagr": f"{r_new['best_by_cagr_index']} ({r_new['cagr']})",
                "old_best_calmar": f"{r_old['best_by_calmar_index']} ({r_old['calmar']})",
                "new_best_calmar": f"{r_new['best_by_calmar_index']} ({r_new['calmar']})",
            })

    print(f"Leaderboard rows with changes: {len(lead_deltas)}")
    for ld in lead_deltas:
        print(f"  [{ld['strategy']} | {ld['track']}]")
        print(f"    Best CAGR:   old: {ld['old_best_cagr']} -> new: {ld['new_best_cagr']}")
        print(f"    Best Calmar: old: {ld['old_best_calmar']} -> new: {ld['new_best_calmar']}")

    # Check n>=10 qualification set changes
    print("\n=== N>=10 QUALIFICATION SET CHECK ===")
    old_n10 = set(zip(df_old_rob[(df_old_rob["n_trades_is"] >= 10) & (df_old_rob["n_trades_oos"] >= 10)]["strategy"],
                      df_old_rob[(df_old_rob["n_trades_is"] >= 10) & (df_old_rob["n_trades_oos"] >= 10)]["country"],
                      df_old_rob[(df_old_rob["n_trades_is"] >= 10) & (df_old_rob["n_trades_oos"] >= 10)]["index"]))
    new_n10 = set(zip(df_final_rob[(df_final_rob["n_trades_is"] >= 10) & (df_final_rob["n_trades_oos"] >= 10)]["strategy"],
                      df_final_rob[(df_final_rob["n_trades_is"] >= 10) & (df_final_rob["n_trades_oos"] >= 10)]["country"],
                      df_final_rob[(df_final_rob["n_trades_is"] >= 10) & (df_final_rob["n_trades_oos"] >= 10)]["index"]))

    print(f"Old n>=10 qualifying count: {len(old_n10)}")
    print(f"New n>=10 qualifying count: {len(new_n10)}")
    moved_in = new_n10 - old_n10
    moved_out = old_n10 - new_n10
    print(f"Moved into n>=10: {moved_in if moved_in else 'None'}")
    print(f"Moved out of n>=10: {moved_out if moved_out else 'None'}")

    # Recompute leaderboard_n10.csv
    n10_leaderboard_rows = []
    for strat in CANONICAL_BATTERY:
        strat_name = strat.name
        for trk in tracks_order:
            sub = df_final_summary[(df_final_summary["strategy"] == strat_name) & (df_final_summary["track"] == trk)]
            qual_sub = sub[sub.apply(lambda r: (r["strategy"], r["country"], r["index"]) in new_n10, axis=1)]
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
            else:
                row_data = {
                    "strategy": strat_name,
                    "track": trk,
                    "best_by_cagr_index": "N/A (0 pairs qualify n>=10)",
                    "cagr": "N/A",
                    "best_by_calmar_index": "N/A (0 pairs qualify n>=10)",
                    "calmar": "N/A",
                }
            n10_leaderboard_rows.append(row_data)

    df_new_lead_n10 = pd.DataFrame(n10_leaderboard_rows)
    df_new_lead_n10.to_csv(base_dir / "leaderboard_n10.csv", index=False)
    print(f"Updated leaderboard_n10.csv: {len(df_new_lead_n10)} rows")

    # Check n10 active vs passive
    loses_to_passive = 0
    for s, c, i in new_n10:
        d_cagr = df_final_summary[(df_final_summary["strategy"] == s) & (df_final_summary["country"] == c) & (df_final_summary["index"] == i) & (df_final_summary["track"] == "Net-Discount")]["CAGR"].iloc[0]
        b_cagr = df_final_summary[(df_final_summary["strategy"] == s) & (df_final_summary["country"] == c) & (df_final_summary["index"] == i) & (df_final_summary["track"] == "Buy-and-Hold")]["CAGR"].iloc[0]
        if d_cagr < b_cagr:
            loses_to_passive += 1

    pct_loses = (loses_to_passive / len(new_n10)) * 100
    print(f"\n=== ACTIVE VS PASSIVE ON N>=10 ===")
    print(f"Loses to passive: {loses_to_passive} of {len(new_n10)} ({pct_loses:.2f}%)")

    # Regenerate n10_full_detail.csv and fdr_corrected_significance.csv
    print("\n=== UPDATING N10_FULL_DETAIL.CSV AND FDR SIGNIFICANCE ===")
    # Run generate_n10_full_detail.py logic for France
    from scripts.generate_n10_full_detail import main as run_n10_detail
    run_n10_detail()
    from scripts.compute_fdr_significance import main as run_fdr
    run_fdr()


if __name__ == "__main__":
    main()
