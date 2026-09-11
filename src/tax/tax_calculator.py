"""Point-in-time tax adjustment calculator."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from .models import TaxRegime
from src.engine.models import Trade, PerformanceMetrics
from src.engine.metrics import compute_performance_metrics


class TaxCalculator:
    """Manages historical tax regimes and point-in-time rate lookups."""

    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)
        self.regimes: List[TaxRegime] = []
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load and normalize tax_dataset.csv."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Tax dataset not found at {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        # Normalize column names
        df.columns = [c.strip().lower() for c in df.columns]

        required_cols = [
            "country",
            "tax_regime_name",
            "rate_type",
            "rate_pct",
            "holding_period_threshold_days",
            "rate_short_pct",
            "rate_long_pct",
            "effective_from",
            "effective_to",
        ]
        for rc in required_cols:
            if rc not in df.columns:
                raise ValueError(f"tax_dataset.csv missing required column: '{rc}'")

        df["effective_from"] = pd.to_datetime(df["effective_from"]).dt.tz_localize(None)
        df["effective_to"] = pd.to_datetime(df["effective_to"].fillna("2099-12-31")).dt.tz_localize(None)

        for _, row in df.iterrows():
            exemption = float(row.get("exemption_threshold_local_currency", 0.0) or 0.0)
            regime = TaxRegime(
                country=str(row["country"]).strip(),
                tax_regime_name=str(row["tax_regime_name"]).strip(),
                rate_type=str(row["rate_type"]).strip().lower(),
                rate_pct=float(row["rate_pct"] or 0.0),
                holding_period_threshold_days=int(row["holding_period_threshold_days"] or 0),
                rate_short_pct=float(row["rate_short_pct"] or 0.0),
                rate_long_pct=float(row["rate_long_pct"] or 0.0),
                exemption_threshold_local_currency=exemption,
                effective_from=row["effective_from"],
                effective_to=row["effective_to"],
                source_url=str(row.get("source_url", "")),
                source_type=str(row.get("source_type", "")),
                confidence=str(row.get("confidence", "")),
                notes=str(row.get("notes", "")),
            )
            self.regimes.append(regime)

    def find_regime(self, country: str, exit_date: pd.Timestamp) -> Optional[TaxRegime]:
        """
        Point-in-time lookup of active tax regime on exit_date without lookahead.
        """
        country_clean = country.strip().lower()
        exit_ts = pd.Timestamp(exit_date).tz_localize(None)

        matches = [
            r for r in self.regimes
            if r.country.strip().lower() == country_clean
            and r.effective_from <= exit_ts <= r.effective_to
        ]

        if not matches:
            # Look for most recent regime if slightly before/after
            country_regimes = [r for r in self.regimes if r.country.strip().lower() == country_clean]
            if country_regimes:
                # Return closest by effective_from
                return sorted(country_regimes, key=lambda x: abs((x.effective_from - exit_ts).days))[0]
            return None

        # If multiple, sort by effective_from descending (most recent rule)
        matches.sort(key=lambda x: x.effective_from, reverse=True)
        return matches[0]

    def calculate_trade_tax(self, trade: Trade, country: str) -> float:
        """
        Calculate capital gains tax for a realized trade.
        Applied to realized gains only (gross_pnl > 0).
        """
        if trade.gross_pnl <= 0:
            return 0.0

        regime = self.find_regime(country, trade.exit_date)
        if not regime:
            return 0.0

        taxable_gain = max(0.0, trade.gross_pnl - regime.exemption_threshold_local_currency)
        if taxable_gain <= 0:
            return 0.0

        if regime.rate_type == "flat":
            tax = taxable_gain * (regime.rate_pct / 100.0)
        elif regime.rate_type == "holding_period_dependent":
            if trade.holding_period_days < regime.holding_period_threshold_days:
                rate = regime.rate_short_pct
            else:
                rate = regime.rate_long_pct
            tax = taxable_gain * (rate / 100.0)
        elif regime.rate_type == "slab_based":
            tax = taxable_gain * (regime.rate_pct / 100.0)
        else:
            tax = taxable_gain * (regime.rate_pct / 100.0)

        return float(round(tax, 4))


def apply_tax_adjustment(
    trades: List[Trade],
    raw_equity_curve: pd.DataFrame,
    country: str,
    tax_calculator: TaxCalculator,
    initial_capital: float = 100000.0,
    risk_free_rate: float = 0.0,
) -> Tuple[List[Trade], pd.DataFrame, PerformanceMetrics]:
    """
    Apply point-in-time tax adjustment to trades and reconstruct post-tax equity curve.
    
    CRITICAL: Does not overwrite pre-tax results; returns adjusted copies.
    """
    # Create independent copies of trades with tax applied
    post_tax_trades: List[Trade] = []
    tax_by_exit_date: Dict[pd.Timestamp, float] = {}

    for t in trades:
        tax = tax_calculator.calculate_trade_tax(t, country)
        new_trade = Trade(
            trade_id=t.trade_id,
            entry_date=t.entry_date,
            entry_price=t.entry_price,
            exit_date=t.exit_date,
            exit_price=t.exit_price,
            shares=t.shares,
            gross_pnl=t.gross_pnl,
            gross_return_pct=t.gross_return_pct,
            holding_period_days=t.holding_period_days,
            entry_fee=t.entry_fee,
            exit_fee=t.exit_fee,
            tax_paid=tax,
            net_pnl=t.gross_pnl - tax - t.entry_fee - t.exit_fee,
        )
        post_tax_trades.append(new_trade)
        tax_by_exit_date[t.exit_date] = tax_by_exit_date.get(t.exit_date, 0.0) + tax

    # Reconstruct path-dependent post-tax equity curve
    if raw_equity_curve.empty:
        return post_tax_trades, raw_equity_curve.copy(), compute_performance_metrics(pd.Series(dtype=float), [])

    post_tax_curve = raw_equity_curve.copy()
    cumulative_tax_paid = 0.0
    adjusted_equity = []

    for date, row in post_tax_curve.iterrows():
        if date in tax_by_exit_date:
            cumulative_tax_paid += tax_by_exit_date[date]
        # Net-of-tax equity reflects cumulative tax removed from portfolio
        adjusted_equity.append(max(0.0, row["equity"] - cumulative_tax_paid))

    post_tax_curve["equity"] = adjusted_equity
    post_tax_metrics = compute_performance_metrics(
        post_tax_curve["equity"],
        post_tax_trades,
        risk_free_rate=risk_free_rate,
    )

    return post_tax_trades, post_tax_curve, post_tax_metrics
