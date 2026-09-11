"""Multi-track simulation coordinator.

Coordinates the 4 required tracks:
1. Gross
2. Net-of-tax
3. Net-of-tax-and-discount-brokerage
4. Net-of-tax-and-full-service-brokerage
Plus Buy & Hold benchmark track through the same tax/brokerage pipeline.
"""

from typing import Tuple
import pandas as pd

from src.data.loader import DataProvenance
from src.engine.models import BacktestResult
from src.engine.backtest import run_backtest_simulation, run_buy_and_hold_benchmark
from src.engine.robustness import evaluate_robustness
from src.tax.tax_calculator import TaxCalculator, apply_tax_adjustment
from src.brokerage.brokerage_calculator import BrokerageCalculator, apply_brokerage_adjustment


import hashlib


def run_multi_track_simulation(
    df: pd.DataFrame,
    signals: pd.Series,
    country: str,
    index_name: str,
    data_source_id: str,
    currency: str,
    provenance: DataProvenance,
    tax_calculator: TaxCalculator,
    brokerage_calculator: BrokerageCalculator,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.0,
    seed: int = 42,
) -> BacktestResult:
    """
    Run full 4-track simulation + benchmark for a single country/index.
    """
    data_start = df.index.min().strftime("%Y-%m-%d")
    data_end = df.index.max().strftime("%Y-%m-%d")

    # 1. Track 1: Gross Strategy Execution
    raw_trades, gross_curve, gross_metrics = run_backtest_simulation(
        df=df,
        signals=signals,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )

    # 2. Track 2: Net-of-Tax
    tax_trades, tax_curve, tax_metrics = apply_tax_adjustment(
        trades=raw_trades,
        raw_equity_curve=gross_curve,
        country=country,
        tax_calculator=tax_calculator,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )

    # 3. Track 3: Net-of-Tax-and-Discount-Brokerage
    disc_trades, disc_curve, disc_metrics = apply_brokerage_adjustment(
        trades=tax_trades,
        tax_adjusted_equity_curve=tax_curve,
        country=country,
        broker_type="discount",
        brokerage_calculator=brokerage_calculator,
        risk_free_rate=risk_free_rate,
    )

    # 4. Track 4: Net-of-Tax-and-Full-Service-Brokerage
    fs_trades, fs_curve, fs_metrics = apply_brokerage_adjustment(
        trades=tax_trades,
        tax_adjusted_equity_curve=tax_curve,
        country=country,
        broker_type="full_service",
        brokerage_calculator=brokerage_calculator,
        risk_free_rate=risk_free_rate,
    )

    # 5. Benchmark: Buy & Hold run through Tax + Discount Brokerage
    bh_trades, bh_raw_curve, _ = run_buy_and_hold_benchmark(
        df=df,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )
    bh_tax_trades, bh_tax_curve, _ = apply_tax_adjustment(
        trades=bh_trades,
        raw_equity_curve=bh_raw_curve,
        country=country,
        tax_calculator=tax_calculator,
        initial_capital=initial_capital,
        risk_free_rate=risk_free_rate,
    )
    _, _, bh_disc_metrics = apply_brokerage_adjustment(
        trades=bh_tax_trades,
        tax_adjusted_equity_curve=bh_tax_curve,
        country=country,
        broker_type="discount",
        brokerage_calculator=brokerage_calculator,
        risk_free_rate=risk_free_rate,
    )

    # 6. Robustness Suite on Discount Track (deterministic seed per index)
    salt = int(hashlib.sha256(f"{country}_{index_name}_{seed}".encode()).hexdigest()[:8], 16)
    index_seed = (seed + salt) % (2**31 - 1)
    robustness = evaluate_robustness(
        trades=disc_trades,
        equity_curve=disc_curve["equity"] if not disc_curve.empty else pd.Series(dtype=float),
        seed=index_seed,
        risk_free_rate=risk_free_rate,
    )

    # 7. Check Exclusion Criteria
    exclusion_reasons = []
    # Exclude if data starts after the initial trading window of 2011 (accounting for Jan 1-2 weekend/holidays)
    if pd.Timestamp(data_start) > pd.Timestamp("2011-01-10"):
        exclusion_reasons.append(f"Late data start: {data_start} (> 2011-01-01)")
    if gross_metrics.total_trades < 5:
        exclusion_reasons.append(f"Insufficient sample: {gross_metrics.total_trades} trades (< 5)")

    exclusion_reason = "; ".join(exclusion_reasons) if exclusion_reasons else None

    # Merge final adjusted trades onto the result (using discount track trades as standard trade detail)
    return BacktestResult(
        country=country,
        index_name=index_name,
        data_source_id=data_source_id,
        currency=currency,
        provenance=provenance,
        data_start=data_start,
        data_end=data_end,
        trades=disc_trades,
        equity_curve=disc_curve,
        gross_metrics=gross_metrics,
        net_tax_metrics=tax_metrics,
        net_discount_metrics=disc_metrics,
        net_full_service_metrics=fs_metrics,
        benchmark_discount_metrics=bh_disc_metrics,
        robustness=robustness,
        exclusion_reason=exclusion_reason,
    )
