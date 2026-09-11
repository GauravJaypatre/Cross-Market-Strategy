"""Unit tests for Robustness & Skeptical Validation Suite."""

import pytest
import pandas as pd
from src.engine.models import Trade
from src.engine.robustness import evaluate_robustness


def test_robustness_is_oos_split_and_guards():
    """Verify IS/OOS split and separate insufficient sample guards."""
    # Construct 4 trades: 2 in IS, 2 in OOS
    trades = [
        Trade(1, pd.Timestamp("2014-01-01"), 100, pd.Timestamp("2014-06-01"), 110, 100, 1000, 0.10, 151),
        Trade(2, pd.Timestamp("2016-01-01"), 110, pd.Timestamp("2016-06-01"), 120, 100, 1000, 0.09, 151),
        Trade(3, pd.Timestamp("2020-01-01"), 120, pd.Timestamp("2020-06-01"), 135, 100, 1500, 0.125, 151),
        Trade(4, pd.Timestamp("2022-01-01"), 135, pd.Timestamp("2022-06-01"), 150, 100, 1500, 0.111, 151),
    ]

    dates = pd.date_range("2011-01-01", "2025-12-31", freq="B")
    equity_curve = pd.Series(100000.0, index=dates)

    rob = evaluate_robustness(trades, equity_curve)

    assert rob.is_trade_count == 2
    assert rob.oos_trade_count == 2
    # IS has 2 trades (< 3) -> should trigger IS guard
    assert rob.is_insufficient_sample is True
    # OOS has 2 trades (>= 2) -> passes OOS guard
    assert rob.oos_insufficient_sample is False


def test_monte_carlo_permutation():
    """Verify Monte Carlo 1,000 run shuffle calculates valid 95th percentile drawdown."""
    trades = [
        Trade(1, pd.Timestamp("2012-01-01"), 100, pd.Timestamp("2012-06-01"), 120, 100, 2000, 0.20, 151),
        Trade(2, pd.Timestamp("2014-01-01"), 120, pd.Timestamp("2014-06-01"), 90, 100, -3000, -0.25, 151),
        Trade(3, pd.Timestamp("2016-01-01"), 90, pd.Timestamp("2016-06-01"), 110, 100, 2000, 0.22, 151),
        Trade(4, pd.Timestamp("2018-01-01"), 110, pd.Timestamp("2018-06-01"), 80, 100, -3000, -0.27, 151),
        Trade(5, pd.Timestamp("2020-01-01"), 80, pd.Timestamp("2020-06-01"), 120, 100, 4000, 0.50, 151),
    ]
    dates = pd.date_range("2011-01-01", "2025-12-31", freq="B")
    equity_curve = pd.Series(100000.0, index=dates)

    rob = evaluate_robustness(trades, equity_curve, num_monte_carlo_runs=500, seed=42)

    assert rob.mc_p95_max_drawdown < 0.0
    # Worst case drawdown should be at least as severe as a single 27% loss
    assert rob.mc_p95_max_drawdown <= -0.27


def test_deterministic_seed_reproducibility():
    """Verify that identical seed produces byte-for-byte identical CI and MC outputs."""
    trades = [
        Trade(1, pd.Timestamp("2012-01-01"), 100, pd.Timestamp("2012-06-01"), 120, 100, 2000, 0.20, 151),
        Trade(2, pd.Timestamp("2014-01-01"), 120, pd.Timestamp("2014-06-01"), 90, 100, -3000, -0.25, 151),
        Trade(3, pd.Timestamp("2016-01-01"), 90, pd.Timestamp("2016-06-01"), 110, 100, 2000, 0.22, 151),
        Trade(4, pd.Timestamp("2018-01-01"), 110, pd.Timestamp("2018-06-01"), 80, 100, -3000, -0.27, 151),
        Trade(5, pd.Timestamp("2020-01-01"), 80, pd.Timestamp("2020-06-01"), 120, 100, 4000, 0.50, 151),
    ]
    dates = pd.date_range("2011-01-01", "2025-12-31", freq="B")
    equity_curve = pd.Series(100000.0, index=dates)

    rob1 = evaluate_robustness(trades, equity_curve, num_monte_carlo_runs=1000, num_bootstrap_samples=1000, seed=42)
    rob2 = evaluate_robustness(trades, equity_curve, num_monte_carlo_runs=1000, num_bootstrap_samples=1000, seed=42)

    assert rob1.cagr_ci_lower == rob2.cagr_ci_lower
    assert rob1.cagr_ci_upper == rob2.cagr_ci_upper
    assert rob1.mc_p95_max_drawdown == rob2.mc_p95_max_drawdown

