import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Long-only cash equity MA crossover strategy.
    Fast: 50 SMA, Slow: 200 SMA.
    Returns pd.Series with values 1 (Long) or 0 (Flat).
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    fast_ma = df['close'].rolling(window=50, min_periods=50).mean()
    slow_ma = df['close'].rolling(window=200, min_periods=200).mean()

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
