"""Unit tests for Module B: Backtest Engine."""

import pytest
import numpy as np
import pandas as pd

from src.engine.backtest import run_backtest_simulation, run_buy_and_hold_benchmark
from src.engine.metrics import compute_performance_metrics, calculate_sharpe, calculate_cagr
from tests.synthetic import generate_synthetic_ohlcv


def test_next_day_open_execution_timing():
    """Verify that Day t close signal is executed strictly at Day t+1 open (no lookahead)."""
    dates = pd.date_range("2020-01-01", periods=4, freq="B")
    df = pd.DataFrame(
        {
            "open": [100.0, 105.0, 110.0, 120.0],
            "high": [102.0, 107.0, 112.0, 122.0],
            "low": [99.0, 104.0, 109.0, 119.0],
            "close": [101.0, 106.0, 111.0, 121.0],
            "volume": [1000] * 4,
        },
        index=pd.DatetimeIndex(dates, name="date"),
    )

    # Signal triggers at index 0 (Day 1 close), exits at index 1 (Day 2 close)
    signals = pd.Series([1, 0, 0, 0], index=df.index)

    trades, equity_curve, metrics = run_backtest_simulation(df, signals, initial_capital=100000.0)

    assert len(trades) == 1
    trade = trades[0]
    # Trade entry should be Day 2 open (105.0), NOT Day 1 close or open!
    assert trade.entry_date == dates[1]
    assert trade.entry_price == 105.0
    # Trade exit should be Day 3 open (110.0)
    assert trade.exit_date == dates[2]
    assert trade.exit_price == 110.0
    assert trade.gross_return_pct == pytest.approx((110.0 - 105.0) / 105.0, 1e-4)


def test_insufficient_sample_guard():
    """Verify that fewer than 5 trades triggers insufficient_sample=True."""
    bars = generate_synthetic_ohlcv(start_date="2020-01-01", end_date="2020-12-31", seed=1)
    # Signal that triggers only 1 trade
    signals = pd.Series(0, index=bars.index)
    signals.iloc[10:30] = 1

    trades, _, metrics = run_backtest_simulation(bars, signals)
    assert len(trades) < 5
    assert metrics.insufficient_sample is True


def test_sharpe_annualization_factor_and_rf():
    """Verify Sharpe formula uses sqrt(252) and specified risk_free_rate."""
    # Synthetic daily returns of constant 0.001
    ret = pd.Series([0.001 + (i % 3 - 1) * 0.005 for i in range(252)])
    sharpe_zero_rf = calculate_sharpe(ret, risk_free_rate=0.0)
    sharpe_high_rf = calculate_sharpe(ret, risk_free_rate=0.05)

    assert sharpe_zero_rf > 0.0
    # Higher risk free rate must reduce Sharpe
    assert sharpe_high_rf < sharpe_zero_rf


def test_buy_and_hold_benchmark(synthetic_bars):
    """Verify Buy & Hold creates exactly one trade from start open to end close."""
    trades, equity_curve, metrics = run_buy_and_hold_benchmark(synthetic_bars, initial_capital=100000.0)
    assert len(trades) == 1
    t = trades[0]
    assert t.entry_date == synthetic_bars.index[0]
    assert t.entry_price == synthetic_bars["open"].iloc[0]
    assert t.exit_date == synthetic_bars.index[-1]
    assert t.exit_price == synthetic_bars["close"].iloc[-1]
    assert len(equity_curve) == len(synthetic_bars)
