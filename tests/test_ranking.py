"""Unit tests for Module E: Ranking and Reporting."""

import json
from pathlib import Path
import pytest
import pandas as pd

from src.data.loader import DataProvenance
from src.engine.models import BacktestResult, PerformanceMetrics
from src.reporting.ranking import partition_and_rank_results
from src.reporting.reporter import generate_reports


def _make_dummy_result(
    country: str,
    index_name: str,
    cagr: float,
    calmar: float,
    trades: int,
    data_start: str = "2011-01-01",
) -> BacktestResult:
    m = PerformanceMetrics(
        cagr=cagr,
        max_drawdown=-0.20,
        sharpe_ratio=0.8,
        calmar_ratio=calmar,
        total_trades=trades,
        win_rate=0.6,
        total_return=1.5,
        annualized_volatility=0.15,
        insufficient_sample=(trades < 5),
    )
    p = DataProvenance(
        vendor="local_csv",
        source_identifier=f"data/{index_name}.csv",
        sha256="dummyhash123456789",
        retrieval_timestamp_utc="2024-01-01T00:00:00Z",
        row_count=3700,
        data_start=data_start,
        data_end="2025-12-31",
    )
    exclusion = None
    if pd.Timestamp(data_start) > pd.Timestamp("2011-01-10"):
        exclusion = f"Late data start: {data_start}"
    elif trades < 5:
        exclusion = f"Insufficient sample: {trades} trades"

    return BacktestResult(
        country=country,
        index_name=index_name,
        data_source_id=f"^{index_name}",
        currency="USD",
        provenance=p,
        data_start=data_start,
        data_end="2025-12-31",
        trades=[],
        equity_curve=pd.DataFrame(),
        gross_metrics=m,
        net_tax_metrics=m,
        net_discount_metrics=m,
        net_full_service_metrics=m,
        benchmark_discount_metrics=m,
        robustness=None,
        exclusion_reason=exclusion,
    )


def test_ranking_and_exclusion_logic():
    """Verify primary sort, secondary Calmar sort, and exclusion partitioning."""
    r1 = _make_dummy_result("United States", "S&P 500", cagr=0.10, calmar=0.50, trades=20)
    r2 = _make_dummy_result("India", "Nifty 50", cagr=0.14, calmar=0.70, trades=25)
    r3 = _make_dummy_result("Germany", "DAX", cagr=0.08, calmar=0.80, trades=15)  # High Calmar, lower CAGR
    # Excluded items:
    r_late = _make_dummy_result("China", "STAR 50", cagr=0.20, calmar=1.0, trades=20, data_start="2019-07-22")
    r_few = _make_dummy_result("Japan", "TOPIX", cagr=0.05, calmar=0.3, trades=3)

    results = [r1, r2, r3, r_late, r_few]

    primary, calmar, excluded = partition_and_rank_results(results)

    # 1. Exclusion verification
    assert len(excluded) == 2
    assert {e.index_name for e in excluded} == {"STAR 50", "TOPIX"}

    # 2. Primary ranking verification (by CAGR descending)
    assert len(primary) == 3
    assert [p.index_name for p in primary] == ["Nifty 50", "S&P 500", "DAX"]

    # 3. Secondary ranking verification (by Calmar descending)
    assert len(calmar) == 3
    assert [c.index_name for c in calmar] == ["DAX", "Nifty 50", "S&P 500"]


def test_report_generation(tmp_path):
    """Verify that JSON, Markdown, and HTML reports are generated with required content."""
    r1 = _make_dummy_result("United States", "S&P 500", cagr=0.10, calmar=0.50, trades=20)
    r_late = _make_dummy_result("China", "STAR 50", cagr=0.20, calmar=1.0, trades=20, data_start="2019-07-22")

    reports = generate_reports([r1, r_late], audit_record=None, output_dir=tmp_path)

    assert reports["json"].exists()
    assert reports["markdown"].exists()
    assert reports["html"].exists()

    # Check JSON
    with open(reports["json"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["primary_ranking_cagr"]) == 1
    assert len(data["appendix_excluded"]) == 1

    # Check Markdown
    with open(reports["markdown"], "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "Primary Ranking" in md_text
    assert "Secondary Ranking" in md_text
    assert "Appendix" in md_text
    assert "Methodological Disclosures" in md_text

    # Check HTML
    with open(reports["html"], "r", encoding="utf-8") as f:
        html_text = f.read()
    assert "<!DOCTYPE html>" in html_text
    assert "S&P 500" in html_text
    assert "STAR 50" in html_text
