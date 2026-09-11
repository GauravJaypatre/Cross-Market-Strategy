"""Python code generator for trading strategies across multiple algorithmic families."""

from typing import Dict, Any
from .models import ParsedStrategy, IndicatorSpec


def generate_ma_crossover_code(fast_period: int, slow_period: int, ma_type: str = "SMA") -> str:
    """Generate deterministic code for MA crossover strategy."""
    if ma_type.upper() == "EMA":
        calc_fast = f"df['close'].ewm(span={fast_period}, adjust=False).mean()"
        calc_slow = f"df['close'].ewm(span={slow_period}, adjust=False).mean()"
    else:
        calc_fast = f"df['close'].rolling(window={fast_period}, min_periods={fast_period}).mean()"
        calc_slow = f"df['close'].rolling(window={slow_period}, min_periods={slow_period}).mean()"

    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Long-only cash equity MA crossover strategy.
    Fast: {fast_period} {ma_type}, Slow: {slow_period} {ma_type}.
    Returns pd.Series with values 1 (Long) or 0 (Flat).
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    fast_ma = {calc_fast}
    slow_ma = {calc_slow}

    signal = pd.Series(0, index=df.index, dtype=int)
    is_long = False

    # State machine for long/flat positions
    for i in range(1, len(df)):
        f_curr = fast_ma.iloc[i]
        s_curr = slow_ma.iloc[i]
        f_prev = fast_ma.iloc[i-1]
        s_prev = slow_ma.iloc[i-1]

        if pd.isna(f_curr) or pd.isna(s_curr) or pd.isna(f_prev) or pd.isna(s_prev):
            continue

        # Buy condition: fast crosses above slow
        if not is_long and (f_curr > s_curr) and (f_prev <= s_prev):
            is_long = True
        # Sell condition: fast crosses below slow
        elif is_long and (f_curr < s_curr) and (f_prev >= s_prev):
            is_long = False

        if is_long:
            signal.iloc[i] = 1

    return signal
'''
    return code


def generate_rsi_code(period: int = 14, oversold: float = 30.0, overbought: float = 70.0) -> str:
    """Generate deterministic code for RSI mean-reversion strategy."""
    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    RSI mean-reversion strategy. Buy when RSI < {oversold}, exit when RSI > {overbought}.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window={period}, min_periods={period}).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window={period}, min_periods={period}).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    signal = pd.Series(0, index=df.index, dtype=int)
    is_long = False

    for i in range(1, len(df)):
        r_curr = rsi.iloc[i]
        if pd.isna(r_curr):
            continue

        if not is_long and r_curr < {oversold}:
            is_long = True
        elif is_long and r_curr > {overbought}:
            is_long = False

        if is_long:
            signal.iloc[i] = 1

    return signal
'''
    return code


def generate_momentum_code(period: int = 252, rebalance_freq: str = "monthly") -> str:
    """Generate deterministic code for Absolute / Time-Series Momentum."""
    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Absolute Momentum with {rebalance_freq} rebalancing.
    Lookback: {period} trading days (12 months).
    Evaluated at the start of each month: if trailing return > 0, hold 100% equity; else cash.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    trailing_ret = df['close'].pct_change(periods={period})
    signal = pd.Series(0, index=df.index, dtype=int)
    current_pos = 0

    months = pd.Series(df.index.month, index=df.index)
    is_month_start = months != months.shift(1)

    for i in range(len(df)):
        if is_month_start.iloc[i]:
            val = trailing_ret.iloc[i]
            if not pd.isna(val):
                current_pos = 1 if val > 0 else 0
        signal.iloc[i] = current_pos

    return signal
'''
    return code


def generate_calendar_code(entry_month: int = 11, entry_day: int = 1, exit_month: int = 4, exit_day: int = 30) -> str:
    """Generate deterministic code for seasonal calendar window (Nov 1 - Apr 30)."""
    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Seasonal Calendar Effect Strategy (Nov 1 to Apr 30 long, cash otherwise).
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    signal = pd.Series(0, index=df.index, dtype=int)
    months = pd.Series(df.index.month, index=df.index)
    # Holding window: November (11) through April (4)
    holding_mask = months.isin([11, 12, 1, 2, 3, 4])
    signal[holding_mask] = 1
    return signal
'''
    return code


def generate_bollinger_breakout_code(period: int = 20, std_dev: float = 2.0) -> str:
    """Generate deterministic code for Bollinger Bands breakout strategy."""
    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Volatility Breakout Strategy (Bollinger Bands).
    Buy when close > upper band (period={period}, std={std_dev}).
    Sell when close < {period}-day midline SMA.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    sma = df['close'].rolling(window={period}, min_periods={period}).mean()
    std = df['close'].rolling(window={period}, min_periods={period}).std()
    upper_band = sma + ({std_dev} * std)

    signal = pd.Series(0, index=df.index, dtype=int)
    is_long = False

    for i in range(1, len(df)):
        c = df['close'].iloc[i]
        ub = upper_band.iloc[i]
        mid = sma.iloc[i]

        if pd.isna(ub) or pd.isna(mid):
            continue

        if not is_long and c > ub:
            is_long = True
        elif is_long and c < mid:
            is_long = False

        if is_long:
            signal.iloc[i] = 1

    return signal
'''
    return code


def generate_drawdown_dip_code(lookback: int = 252, dip_pct: float = 0.10, recovery_pct: float = 0.02) -> str:
    """Generate deterministic code for 52-week high drawdown dip-buying strategy."""
    code = f'''import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Drawdown-Triggered Dip Buying Strategy.
    Buy when price falls >= {dip_pct*100:.0f}% below trailing {lookback}-day high.
    Sell when price recovers to within {recovery_pct*100:.0f}% of that same {lookback}-day high.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    rolling_high = df['close'].rolling(window={lookback}, min_periods={lookback}).max()
    buy_threshold = rolling_high * (1.0 - {dip_pct})
    exit_threshold = rolling_high * (1.0 - {recovery_pct})

    signal = pd.Series(0, index=df.index, dtype=int)
    is_long = False

    for i in range(1, len(df)):
        c = df['close'].iloc[i]
        b_lvl = buy_threshold.iloc[i]
        e_lvl = exit_threshold.iloc[i]

        if pd.isna(b_lvl) or pd.isna(e_lvl):
            continue

        if not is_long and c <= b_lvl:
            is_long = True
        elif is_long and c >= e_lvl:
            is_long = False

        if is_long:
            signal.iloc[i] = 1

    return signal
'''
    return code


def generate_strategy_code(strategy: ParsedStrategy) -> str:
    """Generate or retrieve Python code for parsed strategy across all families."""
    if strategy.generated_code:
        return strategy.generated_code

    ind_names = [ind.name.upper() for ind in strategy.indicators]
    ind_map = {ind.name.upper(): ind.params for ind in strategy.indicators}

    # 1. Bollinger Bands Breakout
    if "BOLLINGERBANDS" in ind_map or "BOLLINGER" in ind_names:
        params = ind_map.get("BOLLINGERBANDS") or ind_map.get("BOLLINGER", {})
        p = params.get("period", 20)
        s = params.get("std_dev", 2.0)
        return generate_bollinger_breakout_code(period=p, std_dev=s)

    # 2. Drawdown Dip Buying (RollingMax / 52-week high)
    if "ROLLINGMAX" in ind_map or "52-WEEK HIGH" in strategy.name.upper() or "DIP" in strategy.name.upper():
        params = ind_map.get("ROLLINGMAX", strategy.parameters)
        lookback = params.get("period", 252)
        dip = params.get("dip_pct", 0.10)
        rec = params.get("recovery_pct", 0.02)
        return generate_drawdown_dip_code(lookback=lookback, dip_pct=dip, recovery_pct=rec)

    # 3. Absolute Momentum (ROC / Trailing Return)
    if "ROC" in ind_map or "MOMENTUM" in strategy.name.upper() or "TRAILING" in strategy.description.lower():
        params = ind_map.get("ROC", strategy.parameters)
        p = params.get("period", 252)
        rf = params.get("rebalance_freq", "monthly")
        return generate_momentum_code(period=p, rebalance_freq=rf)

    # 4. Calendar Effect (Zero technical indicators)
    if len(strategy.indicators) == 0 or "CALENDAR" in strategy.name.upper() or "SEASONAL" in strategy.name.upper():
        return generate_calendar_code()

    # 5. RSI Mean Reversion
    if "RSI" in ind_map:
        params = ind_map["RSI"]
        return generate_rsi_code(
            period=params.get("period", 14),
            oversold=params.get("oversold", 30.0),
            overbought=params.get("overbought", 70.0),
        )

    # 6. Moving Average Crossover (Default fallback)
    if "SMA" in ind_map or "EMA" in ind_map:
        ma_type = "EMA" if "EMA" in ind_map else "SMA"
        params = ind_map.get(ma_type, strategy.parameters)
        fast = params.get("fast_period", 50)
        slow = params.get("slow_period", 200)
        return generate_ma_crossover_code(fast, slow, ma_type)

    return generate_ma_crossover_code(50, 200, "SMA")
