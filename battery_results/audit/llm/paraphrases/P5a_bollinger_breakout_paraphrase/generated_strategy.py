import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.Series:
    """
    Volatility Breakout Strategy (Bollinger Bands).
    Buy when close > upper band (period=20, std=2.0).
    Sell when close < 20-day midline SMA.
    """
    if len(df) == 0:
        return pd.Series(dtype=int)

    sma = df['close'].rolling(window=20, min_periods=20).mean()
    std = df['close'].rolling(window=20, min_periods=20).std()
    upper_band = sma + (2.0 * std)

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
