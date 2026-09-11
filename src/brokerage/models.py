"""Brokerage fee schedule models."""

from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass(frozen=True)
class BrokerSchedule:
    """Represents a point-in-time brokerage commission schedule."""
    country: str
    broker_name: str
    broker_type: str  # 'discount' | 'full_service'
    fee_model: str    # 'flat_per_trade' | 'pct_of_trade_value' | 'pct_with_min_max'
    flat_fee_local_currency: float
    pct_fee: float
    min_fee_local_currency: float
    max_fee_local_currency: float
    fee_tax_rate_pct: float
    other_charges_pct: float
    effective_from: pd.Timestamp
    effective_to: pd.Timestamp
    source_url: Optional[str] = None
    confidence: Optional[str] = None
    selection_criterion: Optional[str] = None
    selection_basis_date: Optional[str] = None
