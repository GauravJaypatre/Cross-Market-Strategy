"""Synthetic OHLCV data generator.

WARNING: This module is strictly walled off to unit tests and test fixtures.
It MUST NEVER be imported by or used within production pipelines (src/).
"""

from datetime import datetime
from typing import Optional
import numpy as np
import pandas as pd


def generate_synthetic_ohlcv(
    start_date: str = "2011-01-01",
    end_date: str = "2025-12-31",
    start_price: float = 1000.0,
    annual_drift: float = 0.08,
    annual_vol: float = 0.18,
    seed: Optional[int] = 42,
    regime: str = "trend_and_cycle",
) -> pd.DataFrame:
    """
    Generate realistic synthetic daily OHLCV bars.
    
    regime:
      - 'trend_and_cycle': creates trends with cyclical waves suitable for crossover testing
      - 'flat': low drift, oscillating around start_price
      - 'bear': negative drift
    """
    if seed is not None:
        np.random.seed(seed)

    dates = pd.date_range(start=start_date, end=end_date, freq="B")  # Business days
    n = len(dates)
    if n == 0:
        raise ValueError("Date range produced 0 business days.")

    dt = 1.0 / 252.0
    daily_drift = annual_drift * dt
    daily_vol = annual_vol * np.sqrt(dt)

    # Base geometric Brownian motion
    shocks = np.random.normal(daily_drift, daily_vol, n)

    if regime == "trend_and_cycle":
        # Add a couple of long cyclical waves to trigger multiple clear MA crossovers
        t = np.linspace(0, 14 * 2 * np.pi, n)
        cyclical = 0.0015 * np.sin(t) + 0.0008 * np.cos(0.5 * t)
        shocks += cyclical

    log_returns = shocks
    cum_prices = start_price * np.exp(np.cumsum(log_returns))

    # Generate open, high, low, close from the simulated path
    closes = cum_prices
    # Open is close of previous day plus small noise
    opens = np.roll(closes, 1)
    opens[0] = start_price * (1 + np.random.normal(0, 0.002))
    opens[1:] = opens[1:] * (1 + np.random.normal(0, 0.003, n - 1))

    # Highs and lows ensure High >= max(Open, Close) and Low <= min(Open, Close)
    max_oc = np.maximum(opens, closes)
    min_oc = np.minimum(opens, closes)

    high_spread = np.abs(np.random.normal(0.005, 0.003, n)) * closes
    low_spread = np.abs(np.random.normal(0.005, 0.003, n)) * closes

    highs = max_oc + high_spread
    lows = np.maximum(0.01, min_oc - low_spread)

    # Volume: lognormal around 1,000,000
    volumes = np.random.lognormal(mean=14.0, sigma=0.4, size=n)

    df = pd.DataFrame(
        {
            "open": np.round(opens, 2),
            "high": np.round(highs, 2),
            "low": np.round(lows, 2),
            "close": np.round(closes, 2),
            "volume": np.round(volumes, 0),
        },
        index=pd.DatetimeIndex(dates, name="date"),
    )

    return df
