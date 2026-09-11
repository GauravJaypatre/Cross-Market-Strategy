"""Command-Line Interface for the Cross-Market Strategy Backtesting System.

Usage:
  python run_backtest.py --strategy "<text>" --universe universe.yaml --tax tax_dataset.csv --brokerage brokerage_dataset.csv --out results/
"""

import argparse
import logging
from pathlib import Path
import sys
import pandas as pd
import numpy as np

from src.config import load_universe
from src.data.loader import load_index_data, DataSourceError
from src.parser.llm_parser import StrategyParser
from src.parser.validator import StrategyRejectedError
from src.tax.tax_calculator import TaxCalculator
from src.brokerage.brokerage_calculator import BrokerageCalculator
from src.multi_track.track_simulator import run_multi_track_simulation
from src.reporting.reporter import generate_reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("CrossMarketBacktest")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Cross-Market Strategy Backtesting & Real-World Friction Evaluation Engine."
    )
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help="Plain-English trading strategy description.",
    )
    parser.add_argument(
        "--universe",
        type=str,
        required=True,
        help="Path to universe.yaml configuration file.",
    )
    parser.add_argument(
        "--tax",
        type=str,
        required=True,
        help="Path to tax_dataset.csv.",
    )
    parser.add_argument(
        "--brokerage",
        type=str,
        required=True,
        help="Path to brokerage_dataset.csv.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="results",
        help="Directory to save final reports and audit artifacts.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing local OHLCV CSV/parquet files.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2011-01-01",
        help="Backtest start date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2025-12-31",
        help="Backtest end date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Starting portfolio capital in local currency.",
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        default=0.0,
        help="Annualized risk-free rate for Sharpe calculation (default 0.0).",
    )
    parser.add_argument(
        "--parser-backend",
        type=str,
        default="auto",
        choices=["auto", "llm", "rule_based"],
        help="Backend for strategy parsing ('auto', 'llm', or 'rule_based').",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="LLM model identifier for strategy parsing (default: gemini-2.5-flash).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Pinned temperature for deterministic LLM parsing (default: 0.0).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Fixed random seed for deterministic Monte Carlo trade-shuffle and bootstrap CI resampling (default: 42).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out)
    audit_dir = out_dir / "audit"
    trades_dir = out_dir / "trades"
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    trades_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=================================================================")
    logger.info("CROSS-MARKET STRATEGY BACKTESTING SYSTEM")
    logger.info("=================================================================")
    logger.info(f"Strategy Text: '{args.strategy}'")
    logger.info(f"Universe Config: {args.universe}")
    logger.info(f"Tax Dataset: {args.tax}")
    logger.info(f"Brokerage Dataset: {args.brokerage}")
    logger.info(f"Output Directory: {out_dir}")
    logger.info(f"Annualized Risk-Free Rate: {args.risk_free_rate * 100:.2f}% (Sharpe 252-day annualization)")
    logger.info(f"Random Seed: {args.seed} (deterministic Monte Carlo & bootstrap)")

    # 1. Module A: Strategy Parsing & Scope Validation
    logger.info("Parsing strategy and validating long-only cash equity scope...")
    parser = StrategyParser(
        backend=args.parser_backend,
        model_name=args.model,
        temperature=args.temperature,
    )

    try:
        parsed_strategy, audit_record = parser.parse(args.strategy, audit_dir=audit_dir)
    except StrategyRejectedError as e:
        logger.error(f"STRATEGY SCOPE VIOLATION: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Strategy parsing failed: {e}")
        sys.exit(1)

    logger.info(f"Strategy parsed successfully: '{parsed_strategy.name}'")
    logger.info(f"Backend Used: {audit_record.parser_backend_used}")
    logger.info(f"Audit saved to {audit_dir}")

    # Compile the generated signal generation function
    local_env = {}
    exec(parsed_strategy.generated_code, {"pd": pd, "np": np}, local_env)
    generate_signals_fn = local_env["generate_signals"]

    # 2. Load Datasets & Universe
    logger.info("Loading universe, tax rules, and brokerage schedules...")
    universe_items = load_universe(args.universe)
    tax_calc = TaxCalculator(args.tax)
    broker_calc = BrokerageCalculator(args.brokerage)
    logger.info(f"Loaded {len(universe_items)} target indices across countries.")

    # 3. Execution Pipeline across Universe
    results = []
    failed_loads = []

    for item in universe_items:
        logger.info(f"Processing {item.country} - {item.index_name} (ID: {item.data_source_id})...")
        try:
            df, provenance = load_index_data(
                data_source_id=item.data_source_id,
                country=item.country,
                index_name=item.index_name,
                start_date=args.start_date,
                end_date=args.end_date,
                data_dir=args.data_dir,
            )
        except DataSourceError as e:
            logger.error(f"Failed loading data for {item.index_name}: {e}")
            failed_loads.append((item, str(e)))
            continue

        # Run signal generator
        signals = generate_signals_fn(df)

        # Run multi-track simulation (Gross, Net-Tax, Net-Discount, Net-Full-Service, Benchmark)
        res = run_multi_track_simulation(
            df=df,
            signals=signals,
            country=item.country,
            index_name=item.index_name,
            data_source_id=item.data_source_id,
            currency=item.currency,
            provenance=provenance,
            tax_calculator=tax_calc,
            brokerage_calculator=broker_calc,
            initial_capital=args.initial_capital,
            risk_free_rate=args.risk_free_rate,
            seed=args.seed,
        )

        results.append(res)

        # Save individual index trade log
        clean_country = item.country.replace(" ", "_").lower()
        clean_index = item.index_name.replace(" ", "_").lower()
        trade_log_df = pd.DataFrame([t.to_dict() for t in res.trades])
        trade_log_path = trades_dir / f"{clean_country}_{clean_index}_trades.csv"
        trade_log_df.to_csv(trade_log_path, index=False)

    if not results:
        logger.error("No indices were successfully backtested. Exiting.")
        sys.exit(1)

    # 4. Generate Reports (JSON, Markdown, HTML)
    logger.info("Generating ranking reports and audit summaries...")
    report_paths = generate_reports(
        results=results,
        audit_record=audit_record,
        output_dir=out_dir,
        seed=args.seed,
    )

    logger.info("=================================================================")
    logger.info("BACKTEST RUN COMPLETED SUCCESSFULLY")
    logger.info("=================================================================")
    logger.info(f"JSON Report:     {report_paths['json']}")
    logger.info(f"Markdown Report: {report_paths['markdown']}")
    logger.info(f"HTML Report:     {report_paths['html']}")
    logger.info(f"Audit Trail:     {audit_dir}")
    logger.info(f"Trade Logs:      {trades_dir}")


if __name__ == "__main__":
    main()
