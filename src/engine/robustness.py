"""Robustness and Skeptical Validation Suite.

Includes:
1. Train/Test Split: In-Sample (2011-2018) vs Out-of-Sample (2019-2025)
2. Individual insufficient sample guards for IS (< 3 trades) and OOS (< 2 trades)
3. Monte Carlo Trade Reshuffling: 1,000 permutations assessing sequence risk & 95th-percentile Max Drawdown
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from .models import Trade, RobustnessMetrics
from .metrics import calculate_cagr, calculate_max_drawdown, calculate_sharpe


def evaluate_robustness(
    trades: List[Trade],
    equity_curve: pd.Series,
    is_cutoff: str = "2018-12-31",
    oos_start: str = "2019-01-01",
    num_monte_carlo_runs: int = 1000,
    num_bootstrap_samples: int = 1000,
    seed: int = 42,
    risk_free_rate: float = 0.0,
) -> RobustnessMetrics:
    """Evaluate IS/OOS degradation, Monte Carlo sequence risk, and bootstrap estimation uncertainty."""
    # Split trades by entry date
    is_trades = [t for t in trades if t.entry_date <= pd.Timestamp(is_cutoff)]
    oos_trades = [t for t in trades if t.entry_date >= pd.Timestamp(oos_start)]

    is_count = len(is_trades)
    oos_count = len(oos_trades)

    is_insufficient = is_count < 3
    oos_insufficient = oos_count < 2

    # Split equity curves
    is_eq = equity_curve.loc[:is_cutoff]
    oos_eq = equity_curve.loc[oos_start:]

    def _eval_sub_curve(sub_eq: pd.Series):
        if len(sub_eq) < 2:
            return 0.0, 0.0, 0.0
        c_days = (sub_eq.index[-1] - sub_eq.index[0]).days
        cagr = calculate_cagr(float(sub_eq.iloc[0]), float(sub_eq.iloc[-1]), max(1, c_days))
        mdd = calculate_max_drawdown(sub_eq)
        ret = sub_eq.pct_change().dropna()
        sharpe = calculate_sharpe(ret, risk_free_rate=risk_free_rate)
        return cagr, mdd, sharpe

    is_cagr, is_mdd, is_sharpe = _eval_sub_curve(is_eq)
    oos_cagr, oos_mdd, oos_sharpe = _eval_sub_curve(oos_eq)

    # Raw percentage point difference (OOS - IS)
    delta_cagr = oos_cagr - is_cagr

    # Degradation ratio
    if abs(is_cagr) > 1e-6:
        degradation = oos_cagr / is_cagr
    else:
        degradation = 0.0

    # Monte Carlo Trade Permutations & Bootstrap Confidence Interval on CAGR
    total_trades_count = len(trades)
    is_directional = total_trades_count < 30
    cagr_ci_lower = 0.0
    cagr_ci_upper = 0.0

    if len(trades) >= 2:
        rng = np.random.default_rng(seed)
        trade_returns = np.array([t.gross_return_pct for t in trades])
        mc_drawdowns = []
        boot_cagrs = []

        c_days = max(1, (equity_curve.index[-1] - equity_curve.index[0]).days) if len(equity_curve) >= 2 else 365.25
        years = c_days / 365.25

        # 1. Monte Carlo Trade-Shuffle: Permute trade order without replacement (Sequence Risk)
        for _ in range(num_monte_carlo_runs):
            shuffled = rng.permutation(trade_returns)
            cum_path = np.cumprod(1.0 + shuffled)
            peak = np.maximum.accumulate(cum_path)
            dd = (cum_path - peak) / peak
            mc_drawdowns.append(float(np.min(dd)))

        # 2. Bootstrap Resampling: Resample trades with replacement (Parameter Estimation Uncertainty)
        for _ in range(num_bootstrap_samples):
            boot_sample = rng.choice(trade_returns, size=len(trade_returns), replace=True)
            final_mult = float(np.prod(1.0 + boot_sample))
            if final_mult > 0 and years > 0:
                boot_cagrs.append(final_mult ** (1.0 / years) - 1.0)
            else:
                boot_cagrs.append(-1.0)

        # 95th percentile worst drawdown (5th percentile of drawdown values)
        p95_mdd = float(np.percentile(mc_drawdowns, 5))
        cagr_ci_lower = float(np.percentile(boot_cagrs, 2.5))
        cagr_ci_upper = float(np.percentile(boot_cagrs, 97.5))
    else:
        p95_mdd = 0.0

    return RobustnessMetrics(
        is_trade_count=is_count,
        is_cagr=is_cagr,
        is_max_drawdown=is_mdd,
        is_sharpe=is_sharpe,
        is_insufficient_sample=is_insufficient,
        oos_trade_count=oos_count,
        oos_cagr=oos_cagr,
        oos_max_drawdown=oos_mdd,
        oos_sharpe=oos_sharpe,
        oos_insufficient_sample=oos_insufficient,
        degradation_ratio=degradation,
        delta_cagr_pp=delta_cagr,
        mc_p95_max_drawdown=p95_mdd,
        cagr_ci_lower=cagr_ci_lower,
        cagr_ci_upper=cagr_ci_upper,
        is_directional_only=is_directional,
    )
