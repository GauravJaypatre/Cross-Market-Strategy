"""Core backtest simulation engine.

Guarantees:
- Day t Close signal -> Day t+1 Open execution (strictly zero lookahead bias)
- Long-only cash equity positions
- Starting capital in local currency (no cross-currency conversions)
- Generates granular Trade log and daily mark-to-market EquityCurve
"""

from typing import List, Tuple
import pandas as pd
from .models import Trade, PerformanceMetrics
from .metrics import compute_performance_metrics


def run_backtest_simulation(
    df: pd.DataFrame,
    signals: pd.Series,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.0,
) -> Tuple[List[Trade], pd.DataFrame, PerformanceMetrics]:
    """
    Execute daily bar-by-bar backtest simulation.
    
    Signals: pd.Series of 1 (long) or 0 (flat).
    Execution: Next-day Open execution.
    """
    if df.empty or len(df) < 2:
        empty_trades: List[Trade] = []
        empty_curve = pd.DataFrame(columns=["cash", "holdings", "equity"])
        empty_metrics = compute_performance_metrics(pd.Series(dtype=float), empty_trades)
        return empty_trades, empty_curve, empty_metrics

    # Align signals to df index
    aligned_signals = signals.reindex(df.index).fillna(0).astype(int)

    trades: List[Trade] = []
    daily_records = []

    cash = float(initial_capital)
    shares = 0.0
    in_trade = False
    entry_date: pd.Timestamp = None
    entry_price = 0.0
    trade_id = 0

    dates = df.index
    opens = df["open"].values
    closes = df["close"].values
    sig_vals = aligned_signals.values

    # Pre-shift execution signal: Day t signal executes at Day t+1 open
    for i in range(len(dates)):
        current_date = dates[i]
        curr_open = float(opens[i])
        curr_close = float(closes[i])

        # Execute pending orders from previous bar's signal
        if i > 0:
            target_signal = sig_vals[i - 1]  # Generated at close of i-1

            # Case 1: Enter Long
            if target_signal == 1 and not in_trade:
                entry_date = current_date
                entry_price = curr_open
                if entry_price > 0:
                    shares = cash / entry_price
                    cash = 0.0
                    in_trade = True

            # Case 2: Exit to Flat
            elif target_signal == 0 and in_trade:
                exit_date = current_date
                exit_price = curr_open
                gross_pnl = shares * (exit_price - entry_price)
                gross_ret = (exit_price - entry_price) / entry_price if entry_price > 0 else 0.0
                holding_days = (exit_date - entry_date).days

                trade_id += 1
                trades.append(
                    Trade(
                        trade_id=trade_id,
                        entry_date=entry_date,
                        entry_price=entry_price,
                        exit_date=exit_date,
                        exit_price=exit_price,
                        shares=shares,
                        gross_pnl=gross_pnl,
                        gross_return_pct=gross_ret,
                        holding_period_days=holding_days,
                    )
                )
                cash = shares * exit_price
                shares = 0.0
                in_trade = False

        # Mark-to-market at day's close
        holdings = shares * curr_close
        total_equity = cash + holdings

        daily_records.append(
            {
                "date": current_date,
                "cash": cash,
                "holdings": holdings,
                "equity": total_equity,
                "position": 1 if in_trade else 0,
            }
        )

    # Force close open trade on final bar to account for all positions
    if in_trade:
        final_date = dates[-1]
        final_price = float(closes[-1])
        gross_pnl = shares * (final_price - entry_price)
        gross_ret = (final_price - entry_price) / entry_price if entry_price > 0 else 0.0
        holding_days = (final_date - entry_date).days
        trade_id += 1
        trades.append(
            Trade(
                trade_id=trade_id,
                entry_date=entry_date,
                entry_price=entry_price,
                exit_date=final_date,
                exit_price=final_price,
                shares=shares,
                gross_pnl=gross_pnl,
                gross_return_pct=gross_ret,
                holding_period_days=holding_days,
            )
        )
        cash = shares * final_price
        shares = 0.0

    equity_curve = pd.DataFrame(daily_records).set_index("date")
    metrics = compute_performance_metrics(
        equity_curve["equity"],
        trades,
        risk_free_rate=risk_free_rate,
    )

    return trades, equity_curve, metrics


def run_buy_and_hold_benchmark(
    df: pd.DataFrame,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.0,
) -> Tuple[List[Trade], pd.DataFrame, PerformanceMetrics]:
    """Run passive Buy & Hold benchmark: Enter at Day 1 Open, exit at final bar Close."""
    if df.empty or len(df) < 2:
        return [], pd.DataFrame(), compute_performance_metrics(pd.Series(dtype=float), [])

    entry_date = df.index[0]
    entry_price = float(df["open"].iloc[0])
    shares = initial_capital / entry_price if entry_price > 0 else 0.0

    exit_date = df.index[-1]
    exit_price = float(df["close"].iloc[-1])
    gross_pnl = shares * (exit_price - entry_price)
    gross_ret = (exit_price - entry_price) / entry_price if entry_price > 0 else 0.0
    holding_days = (exit_date - entry_date).days

    trades = [
        Trade(
            trade_id=1,
            entry_date=entry_date,
            entry_price=entry_price,
            exit_date=exit_date,
            exit_price=exit_price,
            shares=shares,
            gross_pnl=gross_pnl,
            gross_return_pct=gross_ret,
            holding_period_days=holding_days,
        )
    ]

    daily_equity = shares * df["close"]
    daily_records = pd.DataFrame(
        {
            "cash": 0.0,
            "holdings": daily_equity,
            "equity": daily_equity,
            "position": 1,
        },
        index=df.index,
    )

    metrics = compute_performance_metrics(
        daily_records["equity"],
        trades,
        risk_free_rate=risk_free_rate,
    )

    return trades, daily_records, metrics
