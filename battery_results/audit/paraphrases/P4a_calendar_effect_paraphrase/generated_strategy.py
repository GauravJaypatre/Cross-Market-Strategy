import pandas as pd
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
