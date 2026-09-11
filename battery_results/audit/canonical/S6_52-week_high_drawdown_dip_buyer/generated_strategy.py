import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Drawdown-Triggered Dip Buying Strategy.
    Buy when price falls >= 10% below trailing 252-day high.
    Sell when price recovers to within 2% of that same 252-day high.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    rolling_high = df['close'].rolling(window=252, min_periods=252).max()
    buy_threshold = rolling_high * (1.0 - 0.1)
    exit_threshold = rolling_high * (1.0 - 0.02)

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
