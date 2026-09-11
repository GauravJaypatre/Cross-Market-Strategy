"""Point-in-time brokerage cost adjustment calculator."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from .models import BrokerSchedule
from src.engine.models import Trade, PerformanceMetrics
from src.engine.metrics import compute_performance_metrics


class BrokerageCalculator:
    """Manages historical brokerage fee schedules and calculates point-in-time costs."""

    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)
        self.schedules: List[BrokerSchedule] = []
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load and normalize brokerage_dataset.csv."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Brokerage dataset not found at {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        df.columns = [c.strip().lower() for c in df.columns]

        required_cols = [
            "country",
            "broker_name",
            "broker_type",
            "fee_model",
            "effective_from",
            "effective_to",
        ]
        for rc in required_cols:
            if rc not in df.columns:
                raise ValueError(f"brokerage_dataset.csv missing required column: '{rc}'")

        df["effective_from"] = pd.to_datetime(df["effective_from"]).dt.tz_localize(None)
        df["effective_to"] = pd.to_datetime(df["effective_to"].fillna("2099-12-31")).dt.tz_localize(None)

        for _, row in df.iterrows():
            sched = BrokerSchedule(
                country=str(row["country"]).strip(),
                broker_name=str(row["broker_name"]).strip(),
                broker_type=str(row["broker_type"]).strip().lower(),
                fee_model=str(row["fee_model"]).strip().lower(),
                flat_fee_local_currency=float(row.get("flat_fee_local_currency", 0.0) or 0.0),
                pct_fee=float(row.get("pct_fee", 0.0) or 0.0),
                min_fee_local_currency=float(row.get("min_fee_local_currency", 0.0) or 0.0),
                max_fee_local_currency=float(row.get("max_fee_local_currency", 0.0) or 0.0),
                fee_tax_rate_pct=float(row.get("fee_tax_rate_pct", 0.0) or 0.0),
                other_charges_pct=float(row.get("other_charges_pct", 0.0) or 0.0),
                effective_from=row["effective_from"],
                effective_to=row["effective_to"],
                source_url=str(row.get("source_url", "")),
                confidence=str(row.get("confidence", "")),
                selection_criterion=str(row.get("selection_criterion", "")),
                selection_basis_date=str(row.get("selection_basis_date", "")),
            )
            self.schedules.append(sched)

    def find_schedule(
        self,
        country: str,
        broker_type: str,
        trade_date: pd.Timestamp,
    ) -> Optional[BrokerSchedule]:
        """Point-in-time schedule lookup without lookahead bias."""
        country_clean = country.strip().lower()
        btype_clean = broker_type.strip().lower()
        trade_ts = pd.Timestamp(trade_date).tz_localize(None)

        matches = [
            s for s in self.schedules
            if s.country.strip().lower() == country_clean
            and s.broker_type == btype_clean
            and s.effective_from <= trade_ts <= s.effective_to
        ]

        if not matches:
            # Fallback to closest effective period for this country and broker_type
            fallback = [
                s for s in self.schedules
                if s.country.strip().lower() == country_clean and s.broker_type == btype_clean
            ]
            if fallback:
                return sorted(fallback, key=lambda x: abs((x.effective_from - trade_ts).days))[0]
            return None

        # Pick most specific/recent
        matches.sort(key=lambda x: x.effective_from, reverse=True)
        return matches[0]

    def calculate_leg_fee(
        self,
        country: str,
        broker_type: str,
        trade_date: pd.Timestamp,
        trade_value: float,
    ) -> float:
        """
        Calculate total execution cost for one trade leg (Entry or Exit).
        Includes base commission, commission tax (VAT/GST), and other charges (stamp/clearing).
        """
        if trade_value <= 0:
            return 0.0

        sched = self.find_schedule(country, broker_type, trade_date)
        if not sched:
            return 0.0

        # 1. Base Commission
        if sched.fee_model == "flat_per_trade":
            base_fee = sched.flat_fee_local_currency
        elif sched.fee_model == "pct_of_trade_value":
            base_fee = trade_value * (sched.pct_fee / 100.0)
        elif sched.fee_model == "pct_with_min_max":
            raw_fee = trade_value * (sched.pct_fee / 100.0)
            min_fee = sched.min_fee_local_currency
            max_fee = sched.max_fee_local_currency
            if min_fee > 0:
                raw_fee = max(raw_fee, min_fee)
            if max_fee > 0:
                raw_fee = min(raw_fee, max_fee)
            base_fee = raw_fee
        else:
            base_fee = trade_value * (sched.pct_fee / 100.0)

        # 2. Tax on Fee (e.g. GST/VAT on brokerage commission)
        fee_tax = base_fee * (sched.fee_tax_rate_pct / 100.0)

        # 3. Other charges on trade value (e.g. Stamp duty, Exchange/SEBI/Clearing fees)
        other_charges = trade_value * (sched.other_charges_pct / 100.0)

        total_leg_fee = base_fee + fee_tax + other_charges
        return float(round(total_leg_fee, 4))


def apply_brokerage_adjustment(
    trades: List[Trade],
    tax_adjusted_equity_curve: pd.DataFrame,
    country: str,
    broker_type: str,  # 'discount' or 'full_service'
    brokerage_calculator: BrokerageCalculator,
    risk_free_rate: float = 0.0,
) -> Tuple[List[Trade], pd.DataFrame, PerformanceMetrics]:
    """
    Apply point-in-time brokerage fees to trades and calculate net-of-tax-and-brokerage curve.
    """
    adjusted_trades: List[Trade] = []
    fees_by_date: Dict[pd.Timestamp, float] = {}

    for t in trades:
        entry_val = t.shares * t.entry_price
        exit_val = t.shares * t.exit_price

        entry_fee = brokerage_calculator.calculate_leg_fee(country, broker_type, t.entry_date, entry_val)
        exit_fee = brokerage_calculator.calculate_leg_fee(country, broker_type, t.exit_date, exit_val)

        new_t = Trade(
            trade_id=t.trade_id,
            entry_date=t.entry_date,
            entry_price=t.entry_price,
            exit_date=t.exit_date,
            exit_price=t.exit_price,
            shares=t.shares,
            gross_pnl=t.gross_pnl,
            gross_return_pct=t.gross_return_pct,
            holding_period_days=t.holding_period_days,
            entry_fee=entry_fee,
            exit_fee=exit_fee,
            tax_paid=t.tax_paid,
            net_pnl=t.gross_pnl - t.tax_paid - entry_fee - exit_fee,
        )
        adjusted_trades.append(new_t)

        fees_by_date[t.entry_date] = fees_by_date.get(t.entry_date, 0.0) + entry_fee
        fees_by_date[t.exit_date] = fees_by_date.get(t.exit_date, 0.0) + exit_fee

    if tax_adjusted_equity_curve.empty:
        return adjusted_trades, tax_adjusted_equity_curve.copy(), compute_performance_metrics(pd.Series(dtype=float), [])

    net_curve = tax_adjusted_equity_curve.copy()
    cumulative_fees = 0.0
    adjusted_equity = []

    for date, row in net_curve.iterrows():
        if date in fees_by_date:
            cumulative_fees += fees_by_date[date]
        adjusted_equity.append(max(0.0, row["equity"] - cumulative_fees))

    net_curve["equity"] = adjusted_equity
    metrics = compute_performance_metrics(
        net_curve["equity"],
        adjusted_trades,
        risk_free_rate=risk_free_rate,
    )

    return adjusted_trades, net_curve, metrics
