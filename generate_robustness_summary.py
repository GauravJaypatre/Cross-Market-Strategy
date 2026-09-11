"""Script to generate results/full_battery/robustness_summary.csv.

Extracts robustness metrics across all 150 pairs from the full battery results.
Columns: strategy, country, index, track, is_cagr, oos_cagr, degradation_ratio,
mc_p95_maxdd, bootstrap_ci_low, bootstrap_ci_high, n_trades_is, n_trades_oos, guard_triggered.
"""

import csv
import json
from pathlib import Path
from typing import Dict, Any, List

from src.parser.battery_specs import CANONICAL_BATTERY


def slugify(text: str) -> str:
    import re
    s = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", s)


def main():
    base_dir = Path("results/full_battery")
    out_csv_path = base_dir / "robustness_summary.csv"

    strat_map = {slugify(f"{s.id}_{s.name}"): s.name for s in CANONICAL_BATTERY}

    rows: List[Dict[str, Any]] = []

    for strat in CANONICAL_BATTERY:
        strat_slug = slugify(f"{strat.id}_{strat.name}")
        report_json_path = base_dir / strat_slug / "report.json"
        if not report_json_path.exists():
            print(f"Warning: {report_json_path} does not exist.")
            continue

        with open(report_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        indices_data = data.get("primary_ranking_cagr", []) + data.get("excluded_indices", [])

        for item in indices_data:
            country = item.get("country", "")
            index_name = item.get("index_name", "")
            rob = item.get("robustness", {})

            is_trades = rob.get("is_trade_count", 0)
            oos_trades = rob.get("oos_trade_count", 0)

            is_guard = rob.get("is_insufficient_sample", False) or (is_trades < 3)
            oos_guard = rob.get("oos_insufficient_sample", False) or (oos_trades < 2)
            guard_triggered = is_guard or oos_guard

            is_cagr = rob.get("is_cagr", 0.0)
            oos_cagr = rob.get("oos_cagr", 0.0)

            if guard_triggered:
                deg_ratio = None
            else:
                deg_ratio = rob.get("degradation_ratio", 0.0)

            rows.append({
                "strategy": strat.name,
                "country": country,
                "index": index_name,
                "track": "Net-Discount",
                "is_cagr": round(is_cagr, 6),
                "oos_cagr": round(oos_cagr, 6),
                "degradation_ratio": round(deg_ratio, 6) if deg_ratio is not None else "N/A",
                "mc_p95_maxdd": round(rob.get("mc_p95_max_drawdown", 0.0), 6),
                "bootstrap_ci_low": round(rob.get("cagr_ci_lower", 0.0), 6),
                "bootstrap_ci_high": round(rob.get("cagr_ci_upper", 0.0), 6),
                "n_trades_is": is_trades,
                "n_trades_oos": oos_trades,
                "guard_triggered": guard_triggered,
            })

    fieldnames = [
        "strategy",
        "country",
        "index",
        "track",
        "is_cagr",
        "oos_cagr",
        "degradation_ratio",
        "mc_p95_maxdd",
        "bootstrap_ci_low",
        "bootstrap_ci_high",
        "n_trades_is",
        "n_trades_oos",
        "guard_triggered",
    ]

    with open(out_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {out_csv_path}")

    # Print summary statistics
    guards_hit = sum(1 for r in rows if r["guard_triggered"])
    print(f"Total pairs: {len(rows)}")
    print(f"Guards hit: {guards_hit}")

    large_deg = [r for r in rows if r["is_cagr"] > 0.15 and r["oos_cagr"] < 0.0]
    print(f"Pairs with IS CAGR > 15% and OOS CAGR < 0: {len(large_deg)}")
    for ld in large_deg:
        print(ld)


if __name__ == "__main__":
    main()
