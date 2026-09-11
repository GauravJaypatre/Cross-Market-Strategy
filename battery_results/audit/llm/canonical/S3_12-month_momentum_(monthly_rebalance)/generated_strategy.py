import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Absolute Momentum with monthly rebalancing.
    Lookback: 252 trading days (12 months).
    Evaluated at the start of each month: if trailing return > 0, hold 100% equity; else cash.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    trailing_ret = df['close'].pct_change(periods=252)
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
