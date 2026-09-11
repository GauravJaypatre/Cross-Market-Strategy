"""Driver script to execute the full canonical strategy battery across the 15-country universe.

Executes all 6 canonical strategy families across 25 indices (150 pairs),
running all 4 friction tracks + Buy-and-Hold benchmark.
Generates:
- results/full_battery/{strat_slug}/{country_index_slug}/report.json, .md, .html
- results/full_battery/{strat_slug}/report.json, .md, .html
- results/full_battery/summary_cross_country.csv
- results/full_battery/exclusion_log.json and .md
- results/full_battery/leaderboard.csv
- results/full_battery/anomaly_log.json and .md
- Seed=42 determinism check on 2 sampled pairs.
"""

import argparse
import csv
import json
import logging
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import load_universe, UniverseItem
from src.data.loader import load_index_data, DataSourceError, DataProvenance
from src.parser.battery_specs import CANONICAL_BATTERY, BatteryStrategy
from src.parser.llm_parser import StrategyParser
from src.parser.validator import StrategyValidator
from src.tax.tax_calculator import TaxCalculator
from src.brokerage.brokerage_calculator import BrokerageCalculator
from src.multi_track.track_simulator import run_multi_track_simulation
from src.reporting.reporter import generate_reports
from src.engine.models import BacktestResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("FullBatteryRunner")


def slugify(text: str) -> str:
    """Generate filesystem-safe lowercase slug."""
    import re
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", s)


def parse_args():
    parser = argparse.ArgumentParser(description="Full Canonical Strategy Battery Runner across Universe.")
    parser.add_argument("--universe", type=str, default="universe.yaml", help="Path to universe.yaml")
    parser.add_argument("--tax", type=str, default="tax_dataset.csv", help="Path to tax_dataset.csv")
    parser.add_argument("--brokerage", type=str, default="brokerage_dataset.csv", help="Path to brokerage_dataset.csv")
    parser.add_argument("--out", type=str, default="results/full_battery", help="Output directory")
    parser.add_argument("--data-dir", type=str, default="data", help="Directory containing OHLCV CSVs")
    parser.add_argument("--start-date", type=str, default="2011-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2025-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--initial-capital", type=float, default=100000.0, help="Initial capital in local currency")
    parser.add_argument("--risk-free-rate", type=float, default=0.0, help="Annualized risk-free rate")
    parser.add_argument("--seed", type=int, default=42, help="Fixed random seed")
    return parser.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=================================================================")
    logger.info("FULL CANONICAL STRATEGY BATTERY EXECUTION")
    logger.info("=================================================================")
    logger.info(f"Universe:        {args.universe}")
    logger.info(f"Tax Dataset:     {args.tax}")
    logger.info(f"Brokerage:       {args.brokerage}")
    logger.info(f"Output Dir:      {out_dir}")
    logger.info(f"Seed:            {args.seed}")

    # 1. Load Universe and Statutory Calculators
    universe_items = load_universe(args.universe)
    tax_calc = TaxCalculator(args.tax)
    broker_calc = BrokerageCalculator(args.brokerage)
    logger.info(f"Loaded {len(universe_items)} target indices across {len(set(u.country for u in universe_items))} countries.")

    # 2. Pre-load / Cache Market Data for all 25 Indices
    logger.info("Pre-loading market data for all indices to memory/cache...")
    cached_market_data: Dict[str, Tuple[pd.DataFrame, DataProvenance]] = {}
    for idx_item in universe_items:
        logger.info(f"Loading data for {idx_item.country} - {idx_item.index_name} ({idx_item.data_source_id})...")
        try:
            df, prov = load_index_data(
                data_source_id=idx_item.data_source_id,
                country=idx_item.country,
                index_name=idx_item.index_name,
                start_date=args.start_date,
                end_date=args.end_date,
                data_dir=data_dir,
            )
            cached_market_data[idx_item.data_source_id] = (df, prov)
            # If loaded via network, cache locally to speed up any re-runs
            if prov.vendor != "local_csv":
                clean_name = idx_item.data_source_id.lstrip("^")
                cache_file = data_dir / f"{clean_name}.csv"
                if not cache_file.exists():
                    df.to_csv(cache_file)
            logger.info(f"  -> Successfully loaded {len(df)} bars ({prov.data_start} to {prov.data_end}) via {prov.vendor}")
        except Exception as e:
            logger.error(f"  -> CRITICAL FAILED to load data for {idx_item.index_name}: {e}")
            sys.exit(1)

    # 3. Parse all 6 Canonical Strategies
    logger.info("Parsing all 6 canonical strategy specifications...")
    rule_parser = StrategyParser(backend="rule_based")
    compiled_strategies = []

    for strat in CANONICAL_BATTERY:
        parsed_strat, audit_rec = rule_parser.parse(strat.strategy_text)
        StrategyValidator.validate_executable_code(parsed_strat.generated_code)
        local_env = {}
        exec(parsed_strat.generated_code, {"pd": pd, "np": np}, local_env)
        generate_signals_fn = local_env["generate_signals"]
        compiled_strategies.append({
            "spec": strat,
            "parsed": parsed_strat,
            "audit": audit_rec,
            "generate_signals": generate_signals_fn,
            "slug": slugify(f"{strat.id}_{strat.name}"),
        })
        logger.info(f"Compiled Strategy {strat.id}: '{strat.name}' ({strat.family})")

    # 4. Execute Full Battery (6 strategies x 25 indices = 150 pairs)
    total_pairs = len(compiled_strategies) * len(universe_items)
    logger.info(f"Executing {total_pairs} (strategy x index) backtests...")

    all_results: List[Dict[str, Any]] = []  # Stores pair metadata and BacktestResult
    summary_rows: List[Dict[str, Any]] = []

    pair_counter = 0

    for strat_info in compiled_strategies:
        strat = strat_info["spec"]
        strat_slug = strat_info["slug"]
        strat_out_dir = out_dir / strat_slug
        strat_out_dir.mkdir(parents=True, exist_ok=True)
        strat_results_list: List[BacktestResult] = []

        logger.info(f"\n--- Strategy [{strat.id}] {strat.name} ({strat.family}) ---")

        for idx_item in universe_items:
            pair_counter += 1
            df, provenance = cached_market_data[idx_item.data_source_id]

            # Generate signals
            signals = strat_info["generate_signals"](df)

            # Run 4-track simulation + benchmark
            res = run_multi_track_simulation(
                df=df,
                signals=signals,
                country=idx_item.country,
                index_name=idx_item.index_name,
                data_source_id=idx_item.data_source_id,
                currency=idx_item.currency,
                provenance=provenance,
                tax_calculator=tax_calc,
                brokerage_calculator=broker_calc,
                initial_capital=args.initial_capital,
                risk_free_rate=args.risk_free_rate,
                seed=args.seed,
            )

            strat_results_list.append(res)
            is_qualified = (res.exclusion_reason is None)

            pair_entry = {
                "pair_id": f"{strat.id}_{idx_item.data_source_id}",
                "strategy_id": strat.id,
                "strategy_name": strat.name,
                "strategy_family": strat.family,
                "strategy_slug": strat_slug,
                "country": idx_item.country,
                "index_name": idx_item.index_name,
                "data_source_id": idx_item.data_source_id,
                "currency": idx_item.currency,
                "result": res,
                "qualified": is_qualified,
                "exclusion_reason": res.exclusion_reason,
            }
            all_results.append(pair_entry)

            # Generate per-(strategy, index) report in pair directory
            pair_slug = slugify(f"{idx_item.country}_{idx_item.index_name}")
            pair_dir = strat_out_dir / pair_slug
            pair_dir.mkdir(parents=True, exist_ok=True)
            generate_reports(
                results=[res],
                audit_record=strat_info["audit"],
                output_dir=pair_dir,
                seed=args.seed,
            )

            # Build rows for summary_cross_country.csv (5 tracks per pair)
            tracks_info = [
                ("Gross", res.gross_metrics),
                ("Net-Tax", res.net_tax_metrics),
                ("Net-Discount", res.net_discount_metrics),
                ("Net-Full-Service", res.net_full_service_metrics),
                ("Buy-and-Hold", res.benchmark_discount_metrics),
            ]

            for track_name, m in tracks_info:
                summary_rows.append({
                    "strategy": strat.name,
                    "country": idx_item.country,
                    "index": idx_item.index_name,
                    "track": track_name,
                    "CAGR": round(m.cagr, 6) if m else 0.0,
                    "MaxDD": round(m.max_drawdown, 6) if m else 0.0,
                    "Calmar": round(m.calmar_ratio, 6) if m else 0.0,
                    "Sharpe": round(m.sharpe_ratio, 6) if m else 0.0,
                    "n_trades": m.total_trades if m else 0,
                    "qualified": is_qualified,
                })

            status_str = "QUALIFIED" if is_qualified else f"EXCLUDED ({res.exclusion_reason})"
            gross_cagr_str = f"{res.gross_metrics.cagr * 100:.2f}%" if res.gross_metrics else "N/A"
            disc_cagr_str = f"{res.net_discount_metrics.cagr * 100:.2f}%" if res.net_discount_metrics else "N/A"
            logger.info(f"[{pair_counter}/{total_pairs}] {strat.id} x {idx_item.country} - {idx_item.index_name}: Gross={gross_cagr_str}, Net-Disc={disc_cagr_str} -> {status_str}")

        # Generate strategy-level consolidated report across all 25 indices
        logger.info(f"Generating strategy-level reports for {strat.name} in {strat_out_dir}...")
        generate_reports(
            results=strat_results_list,
            audit_record=strat_info["audit"],
            output_dir=strat_out_dir,
            seed=args.seed,
        )

    # 5. Write summary_cross_country.csv
    summary_csv_path = out_dir / "summary_cross_country.csv"
    logger.info(f"\nWriting summary cross-country CSV to {summary_csv_path}...")
    fieldnames = ["strategy", "country", "index", "track", "CAGR", "MaxDD", "Calmar", "Sharpe", "n_trades", "qualified"]
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    logger.info(f"Wrote {len(summary_rows)} rows to {summary_csv_path}.")

    # 6. Exclusion Log Generation
    logger.info("\nCompiling exclusion log...")
    excluded_pairs = [p for p in all_results if not p["qualified"]]
    qualified_pairs = [p for p in all_results if p["qualified"]]

    late_start_count = sum(1 for p in excluded_pairs if "Late data start" in (p["exclusion_reason"] or ""))
    insufficient_trades_count = sum(1 for p in excluded_pairs if "Insufficient sample" in (p["exclusion_reason"] or ""))

    summary_line = (
        f"{len(qualified_pairs)} of {total_pairs} pairs qualified, {len(excluded_pairs)} excluded "
        f"(late start: {late_start_count}, insufficient trades: {insufficient_trades_count})."
    )

    exclusion_data = {
        "summary_line": summary_line,
        "total_pairs": total_pairs,
        "qualified_count": len(qualified_pairs),
        "excluded_count": len(excluded_pairs),
        "late_start_count": late_start_count,
        "insufficient_trades_count": insufficient_trades_count,
        "excluded_pairs": [
            {
                "strategy_id": p["strategy_id"],
                "strategy_name": p["strategy_name"],
                "country": p["country"],
                "index_name": p["index_name"],
                "data_source_id": p["data_source_id"],
                "data_start": p["result"].data_start,
                "gross_trades": p["result"].gross_metrics.total_trades if p["result"].gross_metrics else 0,
                "exclusion_reason": p["exclusion_reason"],
            }
            for p in excluded_pairs
        ],
    }

    exclusion_json_path = out_dir / "exclusion_log.json"
    with open(exclusion_json_path, "w", encoding="utf-8") as f:
        json.dump(exclusion_data, f, indent=2)

    exclusion_md_path = out_dir / "exclusion_log.md"
    with open(exclusion_md_path, "w", encoding="utf-8") as f:
        f.write("# Strategy Battery Exclusion Log\n\n")
        f.write(f"**Summary**: {summary_line}\n\n")
        f.write("| Strategy | Country | Index | Ticker | Data Start | Trades | Exclusion Reason |\n")
        f.write("|:---|:---|:---|:---|:---|:---:|:---|\n")
        for ep in exclusion_data["excluded_pairs"]:
            f.write(
                f"| {ep['strategy_name']} | {ep['country']} | {ep['index_name']} | "
                f"`{ep['data_source_id']}` | {ep['data_start']} | {ep['gross_trades']} | {ep['exclusion_reason']} |\n"
            )

    logger.info(f"Exclusion Log: {summary_line}")
    logger.info(f"Saved {exclusion_json_path} and {exclusion_md_path}")

    # 7. Top-Line Leaderboard Table (6 strategies x 5 tracks = 30 rows)
    logger.info("\nGenerating leaderboard table...")
    leaderboard_rows: List[Dict[str, Any]] = []
    tracks_order = ["Gross", "Net-Tax", "Net-Discount", "Net-Full-Service", "Buy-and-Hold"]

    df_summary = pd.DataFrame(summary_rows)

    for strat in CANONICAL_BATTERY:
        strat_name = strat.name
        for trk in tracks_order:
            sub = df_summary[(df_summary["strategy"] == strat_name) & (df_summary["track"] == trk)]
            # Filter to qualified pairs first; if none qualified, evaluate all
            qual_sub = sub[sub["qualified"] == True]
            eval_sub = qual_sub if len(qual_sub) > 0 else sub

            if not eval_sub.empty:
                # Best by CAGR
                best_cagr_row = eval_sub.loc[eval_sub["CAGR"].idxmax()]
                best_cagr_str = f"{best_cagr_row['country']} - {best_cagr_row['index']}"
                best_cagr_val = best_cagr_row["CAGR"]

                # Best by Calmar
                best_calmar_row = eval_sub.loc[eval_sub["Calmar"].idxmax()]
                best_calmar_str = f"{best_calmar_row['country']} - {best_calmar_row['index']}"
                best_calmar_val = best_calmar_row["Calmar"]
            else:
                best_cagr_str = "N/A"
                best_cagr_val = 0.0
                best_calmar_str = "N/A"
                best_calmar_val = 0.0

            leaderboard_rows.append({
                "strategy": strat_name,
                "track": trk,
                "best_by_cagr_index": best_cagr_str,
                "cagr": round(float(best_cagr_val), 6),
                "best_by_calmar_index": best_calmar_str,
                "calmar": round(float(best_calmar_val), 6),
            })

    leaderboard_csv_path = out_dir / "leaderboard.csv"
    with open(leaderboard_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["strategy", "track", "best_by_cagr_index", "cagr", "best_by_calmar_index", "calmar"])
        writer.writeheader()
        writer.writerows(leaderboard_rows)
    logger.info(f"Saved leaderboard table to {leaderboard_csv_path} ({len(leaderboard_rows)} rows).")

    # 8. Anomaly Checks (Inverted Friction & Near-Zero Fee Drag)
    logger.info("\nRunning friction anomaly checks...")
    anomalies: List[Dict[str, Any]] = []

    for p in all_results:
        res = p["result"]
        gross_cagr = res.gross_metrics.cagr if res.gross_metrics else 0.0
        tax_cagr = res.net_tax_metrics.cagr if res.net_tax_metrics else 0.0
        disc_cagr = res.net_discount_metrics.cagr if res.net_discount_metrics else 0.0
        fs_cagr = res.net_full_service_metrics.cagr if res.net_full_service_metrics else 0.0
        trades_count = res.gross_metrics.total_trades if res.gross_metrics else 0

        # Check 1: Inverted Friction (Net-Discount CAGR > Gross CAGR)
        # Allow 1e-6 tolerance for floating point rounding
        if disc_cagr > (gross_cagr + 1e-6):
            anomalies.append({
                "type": "INVERTED_FRICTION_DISCOUNT_GT_GROSS",
                "severity": "CRITICAL",
                "strategy": p["strategy_name"],
                "country": p["country"],
                "index": p["index_name"],
                "gross_cagr": gross_cagr,
                "net_discount_cagr": disc_cagr,
                "cagr_diff": disc_cagr - gross_cagr,
                "trades": trades_count,
                "detail": f"Net-Discount CAGR ({disc_cagr*100:.4f}%) exceeds Gross CAGR ({gross_cagr*100:.4f}%)."
            })

        if tax_cagr > (gross_cagr + 1e-6):
            anomalies.append({
                "type": "INVERTED_FRICTION_TAX_GT_GROSS",
                "severity": "CRITICAL",
                "strategy": p["strategy_name"],
                "country": p["country"],
                "index": p["index_name"],
                "gross_cagr": gross_cagr,
                "net_tax_cagr": tax_cagr,
                "cagr_diff": tax_cagr - gross_cagr,
                "trades": trades_count,
                "detail": f"Net-Tax CAGR ({tax_cagr*100:.4f}%) exceeds Gross CAGR ({gross_cagr*100:.4f}%)."
            })

        # Check 2: Near-Zero Full-Service Fee Drag on active qualified strategies
        # Fee drag = Net-Discount CAGR - Net-Full-Service CAGR
        if p["qualified"] and trades_count >= 5:
            fs_drag = disc_cagr - fs_cagr
            # If Full-Service commission difference produces less than 0.01% (0.0001) annualized drag
            if abs(fs_drag) < 0.0001:
                anomalies.append({
                    "type": "NEAR_ZERO_FULL_SERVICE_FEE_DRAG",
                    "severity": "WARNING",
                    "strategy": p["strategy_name"],
                    "country": p["country"],
                    "index": p["index_name"],
                    "net_discount_cagr": disc_cagr,
                    "net_full_service_cagr": fs_cagr,
                    "drag": fs_drag,
                    "trades": trades_count,
                    "detail": f"Full-Service fee drag ({fs_drag*100:.6f}%) is near-zero despite {trades_count} active trades."
                })

    anomaly_data = {
        "total_anomalies": len(anomalies),
        "critical_count": sum(1 for a in anomalies if a["severity"] == "CRITICAL"),
        "warning_count": sum(1 for a in anomalies if a["severity"] == "WARNING"),
        "anomalies": anomalies,
    }

    anomaly_json_path = out_dir / "anomaly_log.json"
    with open(anomaly_json_path, "w", encoding="utf-8") as f:
        json.dump(anomaly_data, f, indent=2)

    anomaly_md_path = out_dir / "anomaly_log.md"
    with open(anomaly_md_path, "w", encoding="utf-8") as f:
        f.write("# Battery Friction Anomaly Audit Log\n\n")
        if anomalies:
            f.write(f"**Total Anomalies Detected**: {len(anomalies)} (Critical: {anomaly_data['critical_count']}, Warnings: {anomaly_data['warning_count']})\n\n")
            f.write("| Type | Severity | Strategy | Country | Index | Trades | Detail |\n")
            f.write("|:---|:---:|:---|:---|:---|:---:|:---|\n")
            for a in anomalies:
                f.write(f"| `{a['type']}` | **{a['severity']}** | {a['strategy']} | {a['country']} | {a['index']} | {a['trades']} | {a['detail']} |\n")
        else:
            f.write("✅ **Zero Anomalies Detected**. All friction tracks satisfy monotonic drag: Gross >= Net-Tax >= Net-Discount >= Net-Full-Service, and full-service fee schedules generate expected drag across all active qualified pairs.\n")

    logger.info(f"Anomaly Audit: {len(anomalies)} anomalies found.")
    logger.info(f"Saved {anomaly_json_path} and {anomaly_md_path}")

    # 9. Seed=42 Determinism Audit on 2 Randomly Sampled Pairs
    logger.info("\nRunning seed=42 determinism audit on 2 randomly sampled pairs...")
    rng = random.Random(args.seed)
    sampled_pairs = rng.sample(all_results, 2)

    determinism_diffs: List[str] = []

    for sp in sampled_pairs:
        strat_id = sp["strategy_id"]
        strat_info = next(s for s in compiled_strategies if s["spec"].id == strat_id)
        idx_ticker = sp["data_source_id"]
        idx_item = next(u for u in universe_items if u.data_source_id == idx_ticker)
        df, prov = cached_market_data[idx_ticker]

        # Re-run simulation with identical parameters
        signals = strat_info["generate_signals"](df)
        re_res = run_multi_track_simulation(
            df=df,
            signals=signals,
            country=idx_item.country,
            index_name=idx_item.index_name,
            data_source_id=idx_item.data_source_id,
            currency=idx_item.currency,
            provenance=prov,
            tax_calculator=tax_calc,
            brokerage_calculator=broker_calc,
            initial_capital=args.initial_capital,
            risk_free_rate=args.risk_free_rate,
            seed=args.seed,
        )

        orig_res = sp["result"]

        # Diff metrics
        metrics_to_compare = [
            ("Gross CAGR", orig_res.gross_metrics.cagr, re_res.gross_metrics.cagr),
            ("Gross MaxDD", orig_res.gross_metrics.max_drawdown, re_res.gross_metrics.max_drawdown),
            ("Net-Disc CAGR", orig_res.net_discount_metrics.cagr, re_res.net_discount_metrics.cagr),
            ("Net-Disc MaxDD", orig_res.net_discount_metrics.max_drawdown, re_res.net_discount_metrics.max_drawdown),
            ("Net-FS CAGR", orig_res.net_full_service_metrics.cagr, re_res.net_full_service_metrics.cagr),
            ("Total Trades", orig_res.gross_metrics.total_trades, re_res.gross_metrics.total_trades),
        ]

        if orig_res.robustness and re_res.robustness:
            metrics_to_compare.extend([
                ("MC P95 MaxDD", orig_res.robustness.mc_p95_max_drawdown, re_res.robustness.mc_p95_max_drawdown),
                ("Bootstrap CI Lower", orig_res.robustness.cagr_ci_lower, re_res.robustness.cagr_ci_lower),
                ("Bootstrap CI Upper", orig_res.robustness.cagr_ci_upper, re_res.robustness.cagr_ci_upper),
            ])

        for m_name, val1, val2 in metrics_to_compare:
            if abs(val1 - val2) > 1e-12:
                diff_msg = f"{sp['pair_id']} - {m_name}: run1={val1} != run2={val2}"
                determinism_diffs.append(diff_msg)
                logger.error(f"DETERMINISM MISMATCH: {diff_msg}")

        # Check trades length
        if len(orig_res.trades) != len(re_res.trades):
            diff_msg = f"{sp['pair_id']} - Trades count: run1={len(orig_res.trades)} != run2={len(re_res.trades)}"
            determinism_diffs.append(diff_msg)
            logger.error(f"DETERMINISM MISMATCH: {diff_msg}")

    if not determinism_diffs:
        logger.info("DETERMINISM CHECK PASSED: 0 diffs across all sampled pairs and metrics!")
    else:
        logger.error(f"DETERMINISM CHECK FAILED with {len(determinism_diffs)} differences!")

    logger.info("=================================================================")
    logger.info("EXECUTION COMPLETE")
    logger.info(f"Total Pairs Run:     {total_pairs}")
    logger.info(f"Total Qualified:     {len(qualified_pairs)}")
    logger.info(f"Total Excluded:      {len(excluded_pairs)}")
    logger.info(f"Summary Rows:        {len(summary_rows)}")
    logger.info(f"Leaderboard Rows:    {len(leaderboard_rows)}")
    logger.info(f"Anomalies:           {len(anomalies)}")
    logger.info(f"Determinism Diffs:   {len(determinism_diffs)}")
    logger.info("=================================================================")


if __name__ == "__main__":
    main()
