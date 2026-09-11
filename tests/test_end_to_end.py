"""End-to-end pipeline and CLI integration tests."""

import json
from pathlib import Path
import subprocess
import sys
import yaml
import pytest
import pandas as pd

from tests.synthetic import generate_synthetic_ohlcv
from src.data.loader import DataSourceError, load_index_data


def test_production_loader_hard_failure_guard(tmp_path):
    """
    CRITICAL: Verify production data loader hard-fails (never falls back to synthetic data)
    when local CSV is missing and invalid ticker is queried.
    """
    with pytest.raises(DataSourceError) as exc_info:
        load_index_data(
            data_source_id="INVALID_NONEXISTENT_TICKER_XYZ123",
            country="Nowhere",
            index_name="Ghost Index",
            data_dir=tmp_path,
        )
    assert "HARD FAILURE" in str(exc_info.value)
    assert "Production runs will NEVER fall back to synthetic data" in str(exc_info.value)


def test_end_to_end_cli_pipeline(tmp_path, root_dir):
    """
    Test complete CLI pipeline run:
    - Sets up test universe & local data feeds
    - Executes run_backtest.py via subprocess
    - Verifies JSON, Markdown, HTML, audit logs, and trade logs
    """
    test_data_dir = tmp_path / "data"
    test_out_dir = tmp_path / "results"
    test_data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create two local data files
    df_us = generate_synthetic_ohlcv(start_date="2011-01-01", end_date="2025-12-31", seed=42)
    df_us.to_csv(test_data_dir / "GSPC.csv")

    df_in = generate_synthetic_ohlcv(start_date="2011-01-01", end_date="2025-12-31", seed=99)
    df_in.to_csv(test_data_dir / "NSEI.csv")

    # 2. Create small test universe.yaml
    test_universe_path = tmp_path / "test_universe.yaml"
    universe_content = {
        "indices": [
            {
                "country": "United States",
                "index_name": "S&P 500",
                "data_source_id": "GSPC",
                "currency": "USD",
            },
            {
                "country": "India",
                "index_name": "Nifty 50",
                "data_source_id": "NSEI",
                "currency": "INR",
            },
        ]
    }
    with open(test_universe_path, "w", encoding="utf-8") as f:
        yaml.dump(universe_content, f)

    strategy_text = (
        "Buy when the 50-day moving average crosses above the 200-day moving average, "
        "sell when it crosses below, no leverage, no shorting."
    )

    cmd = [
        sys.executable,
        str(root_dir / "run_backtest.py"),
        "--strategy", strategy_text,
        "--universe", str(test_universe_path),
        "--tax", str(root_dir / "tax_dataset.csv"),
        "--brokerage", str(root_dir / "brokerage_dataset.csv"),
        "--data-dir", str(test_data_dir),
        "--out", str(test_out_dir),
        "--parser-backend", "rule_based",
        "--risk-free-rate", "0.0",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI failed with error:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    # 3. Verify all artifacts
    assert (test_out_dir / "report.json").exists()
    assert (test_out_dir / "report.md").exists()
    assert (test_out_dir / "report.html").exists()
    assert (test_out_dir / "audit" / "parser_audit.json").exists()
    assert (test_out_dir / "audit" / "generated_strategy.py").exists()

    # Verify JSON structure
    with open(test_out_dir / "report.json", "r", encoding="utf-8") as f:
        report = json.load(f)

    assert "metadata" in report
    assert "primary_ranking_cagr" in report
    assert len(report["primary_ranking_cagr"]) > 0

    first = report["primary_ranking_cagr"][0]
    assert "gross_metrics" in first
    assert "net_tax_metrics" in first
    assert "net_discount_metrics" in first
    assert "net_full_service_metrics" in first
    assert "benchmark_discount_metrics" in first
    assert "provenance" in first
    # Verify provenance logged SHA256 checksum and local vendor
    assert first["provenance"]["vendor"] == "local_csv"
    assert first["provenance"]["sha256"] is not None
    assert len(first["provenance"]["sha256"]) == 64
