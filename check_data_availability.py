"""Standalone script to empirically audit market data availability across universe.yaml.

Attempts to load each index via the official production loader chain:
  local CSV -> yfinance -> Stooq fallback -> hard failure.

Generates data_availability_report.csv detailing row counts, date ranges, vendors,
and trading day gaps.
"""

import argparse
import csv
from datetime import datetime
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List
import pandas as pd
import yaml

from src.data.loader import load_index_data, DataSourceError


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("DataAvailabilityAuditor")


def compute_trading_gaps(index_dates: pd.DatetimeIndex, max_business_gap: int = 4) -> int:
    """Count gaps where consecutive trading days differ by more than max_business_gap calendar days."""
    if len(index_dates) < 2:
        return 0
    deltas = (index_dates[1:] - index_dates[:-1]).days
    # Gaps exceeding 4 calendar days (e.g. prolonged holiday closures or data outages)
    significant_gaps = sum(1 for d in deltas if d > max_business_gap)
    return significant_gaps


def audit_universe(
    universe_path: Path,
    data_dir: Path,
    start_date: str = "2011-01-01",
    end_date: str = "2025-12-31",
) -> List[Dict[str, Any]]:
    """Audit every index configured in universe.yaml."""
    with open(universe_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    indices = config.get("indices", [])
    logger.info(f"Loaded {len(indices)} indices from {universe_path} to audit.")

    report_rows = []

    for i, idx in enumerate(indices, 1):
        country = idx.get("country", "")
        name = idx.get("index_name", "")
        source_id = idx.get("data_source_id", "")
        currency = idx.get("currency", "")

        logger.info(f"[{i}/{len(indices)}] Checking {country} - {name} ({source_id})...")

        row = {
            "country": country,
            "index_name": name,
            "data_source_id": source_id,
            "currency": currency,
            "status": "FAILED",
            "vendor_used": "none",
            "row_count": 0,
            "data_start": "N/A",
            "data_end": "N/A",
            "gaps_over_4d": 0,
            "usable_for_backtest": False,
            "detail": "",
        }

        try:
            df, provenance = load_index_data(
                data_source_id=source_id,
                country=country,
                index_name=name,
                start_date=start_date,
                end_date=end_date,
                data_dir=data_dir if data_dir.exists() else None,
            )

            gaps = compute_trading_gaps(df.index, max_business_gap=5)
            row["status"] = "LOADED"
            row["vendor_used"] = provenance.vendor
            row["row_count"] = provenance.row_count
            row["data_start"] = provenance.data_start
            row["data_end"] = provenance.data_end
            row["gaps_over_4d"] = gaps

            # Usability guard: >= 2,500 daily bars, starts by 2012, ends at or after 2024
            is_usable = (
                provenance.row_count >= 2500
                and provenance.data_start <= "2012-01-01"
                and provenance.data_end >= "2024-01-01"
            )
            row["usable_for_backtest"] = is_usable
            row["detail"] = f"Successfully loaded via {provenance.vendor} ({provenance.row_count} bars)"
            logger.info(f"  -> SUCCESS ({provenance.vendor}): {provenance.row_count} rows, {provenance.data_start} to {provenance.data_end}")

        except DataSourceError as e:
            row["status"] = "FAILED"
            row["detail"] = str(e).split("\n")[0]
            logger.warning(f"  -> FAILED: {row['detail']}")
        except Exception as e:
            row["status"] = "ERROR"
            row["detail"] = f"Unexpected error: {e}"
            logger.error(f"  -> ERROR: {e}")

        report_rows.append(row)

    return report_rows


def main():
    parser = argparse.ArgumentParser(description="Audit market data availability across universe.yaml.")
    parser.add_argument("--universe", type=str, default="universe.yaml", help="Path to universe.yaml")
    parser.add_argument("--data-dir", type=str, default="data", help="Local data directory for CSV cache")
    parser.add_argument("--out", type=str, default="data_availability_report.csv", help="Output CSV path")
    args = parser.parse_args()

    universe_file = Path(args.universe)
    data_dir = Path(args.data_dir)
    out_file = Path(args.out)

    if not universe_file.exists():
        logger.error(f"Universe file not found: {universe_file}")
        sys.exit(1)

    logger.info("=================================================================")
    logger.info("MARKET DATA AVAILABILITY AUDIT (PRODUCTION LOADER CHAIN)")
    logger.info("=================================================================")

    rows = audit_universe(universe_file, data_dir)

    # Write CSV report
    fieldnames = [
        "country",
        "index_name",
        "data_source_id",
        "currency",
        "status",
        "vendor_used",
        "row_count",
        "data_start",
        "data_end",
        "gaps_over_4d",
        "usable_for_backtest",
        "detail",
    ]

    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("=================================================================")
    logger.info("DATA AVAILABILITY AUDIT SUMMARY")
    logger.info("=================================================================")
    total = len(rows)
    loaded = sum(1 for r in rows if r["status"] == "LOADED")
    usable = sum(1 for r in rows if r["usable_for_backtest"])
    failed = total - loaded

    logger.info(f"Total Indices Audited:    {total}")
    logger.info(f"Successfully Loaded:      {loaded} / {total}")
    logger.info(f"Usable for Full Backtest: {usable} / {total}")
    logger.info(f"Failed / Unavailable:     {failed} / {total}")
    logger.info(f"Audit Report Exported To: {out_file.resolve()}")
    logger.info("=================================================================")


if __name__ == "__main__":
    main()
