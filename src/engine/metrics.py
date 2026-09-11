"""Financial performance metrics calculations.

Methodological disclosures:
- Annualization factor: sqrt(252) trading days.
- Risk-free rate: explicit parameter (default 0.0).
- Calmar ratio: CAGR / abs(max_drawdown).
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from .models import Trade, PerformanceMetrics


def calculate_cagr(start_val: float, end_val: float, days: float) -> float:
    """Calculate Compound Annual Growth Rate over given calendar days."""
    if start_val <= 0 or end_val <= 0 or days <= 0:
        return 0.0
    years = days / 365.25
    if years < (1.0 / 365.25):
        return 0.0
    try:
        cagr = (end_val / start_val) ** (1.0 / years) - 1.0
        return float(cagr)
    except (ZeroDivisionError, OverflowError, ValueError):
        return 0.0


def calculate_max_drawdown(equity_series: pd.Series) -> float:
    """Calculate maximum peak-to-trough drawdown (returns value <= 0)."""
    if len(equity_series) == 0:
        return 0.0
    running_max = equity_series.cummax()
    drawdowns = (equity_series - running_max) / running_max.replace(0, np.nan)
    min_dd = drawdowns.min()
    return float(min_dd) if not pd.isna(min_dd) else 0.0


def calculate_sharpe(
    daily_returns: pd.Series,
    risk_free_rate: float = 0.0,
    annualization_factor: float = np.sqrt(252.0),
) -> float:
    """
    Calculate annualized Sharpe ratio.
    Default risk_free_rate=0.0 (stated simplification for cross-market comparisons).
    """
    clean_returns = daily_returns.dropna()
    if len(clean_returns) < 2:
        return 0.0

    daily_rf = risk_free_rate / 252.0
    excess_returns = clean_returns - daily_rf
    std_dev = excess_returns.std()

    if std_dev == 0 or pd.isna(std_dev):
        return 0.0

    sharpe = (excess_returns.mean() / std_dev) * annualization_factor
    return float(sharpe) if not pd.isna(sharpe) else 0.0


def calculate_calmar(cagr: float, max_drawdown: float) -> float:
    """Calculate Calmar ratio: CAGR / abs(max_drawdown)."""
    dd_abs = abs(max_drawdown)
    if dd_abs < 1e-6:
        return 0.0
    return float(cagr / dd_abs)


def calculate_win_rate(trades: List[Trade]) -> float:
    """Calculate percentage of profitable trades."""
    if not trades:
        return 0.0
    winning = sum(1 for t in trades if t.gross_pnl > 0)
    return float(winning / len(trades))


def compute_performance_metrics(
    equity_curve: pd.Series,
    trades: List[Trade],
    risk_free_rate: float = 0.0,
) -> PerformanceMetrics:
    """Compute complete PerformanceMetrics object from an equity curve series and trade list."""
    if equity_curve.empty:
        return PerformanceMetrics(
            cagr=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            calmar_ratio=0.0,
            total_trades=0,
            win_rate=0.0,
            total_return=0.0,
            annualized_volatility=0.0,
            insufficient_sample=True,
        )

    start_val = float(equity_curve.iloc[0])
    end_val = float(equity_curve.iloc[-1])

    # Calendar days calculation
    calendar_days = (equity_curve.index[-1] - equity_curve.index[0]).days
    if calendar_days <= 0:
        calendar_days = len(equity_curve) * (365.25 / 252.0)

    cagr = calculate_cagr(start_val, end_val, calendar_days)
    max_dd = calculate_max_drawdown(equity_curve)
    calmar = calculate_calmar(cagr, max_dd)

    daily_returns = equity_curve.pct_change().dropna()
    sharpe = calculate_sharpe(daily_returns, risk_free_rate=risk_free_rate)
    ann_vol = float(daily_returns.std() * np.sqrt(252.0)) if len(daily_returns) > 1 else 0.0

    total_return = (end_val - start_val) / start_val if start_val > 0 else 0.0
    total_trades = len(trades)
    win_rate = calculate_win_rate(trades)
    insufficient = total_trades < 5

    return PerformanceMetrics(
        cagr=cagr,
        max_drawdown=max_dd,
        sharpe_ratio=sharpe,
        calmar_ratio=calmar,
        total_trades=total_trades,
        win_rate=win_rate,
        total_return=total_return,
        annualized_volatility=ann_vol,
        insufficient_sample=insufficient,
    )
