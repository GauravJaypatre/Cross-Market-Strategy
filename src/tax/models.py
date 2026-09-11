"""Tax regime schemas."""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass(frozen=True)
class TaxRegime:
    """Represents a point-in-time country resident equity tax schedule."""
    country: str
    tax_regime_name: str
    rate_type: str  # 'flat' | 'holding_period_dependent' | 'slab_based'
    rate_pct: float
    holding_period_threshold_days: int
    rate_short_pct: float
    rate_long_pct: float
    exemption_threshold_local_currency: float
    effective_from: pd.Timestamp
    effective_to: pd.Timestamp
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    confidence: Optional[str] = None
    notes: Optional[str] = None
