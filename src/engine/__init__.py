"""Backtest engine package."""
from .models import Trade, PerformanceMetrics, RobustnessMetrics, BacktestResult
from .metrics import (
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe,
    calculate_calmar,
    compute_performance_metrics,
)
from .robustness import evaluate_robustness
from .backtest import run_backtest_simulation

__all__ = [
    "Trade",
    "PerformanceMetrics",
    "RobustnessMetrics",
    "BacktestResult",
    "calculate_cagr",
    "calculate_max_drawdown",
    "calculate_sharpe",
    "calculate_calmar",
    "compute_performance_metrics",
    "evaluate_robustness",
    "run_backtest_simulation",
]
