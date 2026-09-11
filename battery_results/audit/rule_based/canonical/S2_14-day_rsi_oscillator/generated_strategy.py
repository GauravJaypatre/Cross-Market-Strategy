import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    RSI mean-reversion strategy. Buy when RSI < 30.0, exit when RSI > 70.0.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    signal = pd.Series(0, index=df.index, dtype=int)
    is_long = False

    for i in range(1, len(df)):
        r_curr = rsi.iloc[i]
        if pd.isna(r_curr):
            continue

        if not is_long and r_curr < 30.0:
            is_long = True
        elif is_long and r_curr > 70.0:
            is_long = False

        if is_long:
            signal.iloc[i] = 1

    return signal
