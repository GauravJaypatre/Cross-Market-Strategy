"""Data models for trades, metrics, and backtest results."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import pandas as pd
from src.data.loader import DataProvenance


@dataclass
class Trade:
    """Represents a realized round-trip long cash equity trade."""
    trade_id: int
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float
    shares: float
    gross_pnl: float
    gross_return_pct: float
    holding_period_days: int
    entry_fee: float = 0.0
    exit_fee: float = 0.0
    tax_paid: float = 0.0
    net_pnl: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trade_id": self.trade_id,
            "entry_date": self.entry_date.strftime("%Y-%m-%d"),
            "entry_price": round(float(self.entry_price), 4),
            "exit_date": self.exit_date.strftime("%Y-%m-%d"),
            "exit_price": round(float(self.exit_price), 4),
            "shares": round(float(self.shares), 4),
            "gross_pnl": round(float(self.gross_pnl), 2),
            "gross_return_pct": round(float(self.gross_return_pct), 4),
            "holding_period_days": int(self.holding_period_days),
            "entry_fee": round(float(self.entry_fee), 2),
            "exit_fee": round(float(self.exit_fee), 2),
            "tax_paid": round(float(self.tax_paid), 2),
            "net_pnl": round(float(self.net_pnl), 2),
        }


@dataclass
class PerformanceMetrics:
    """Core financial performance metrics for an equity curve."""
    cagr: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    total_trades: int
    win_rate: float
    total_return: float
    annualized_volatility: float
    insufficient_sample: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cagr": round(self.cagr, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "sharpe_ratio": round(self.sharpe_ratio, 4),
            "calmar_ratio": round(self.calmar_ratio, 4),
            "total_trades": self.total_trades,
            "win_rate": round(self.win_rate, 4),
            "total_return": round(self.total_return, 4),
            "annualized_volatility": round(self.annualized_volatility, 4),
            "insufficient_sample": self.insufficient_sample,
        }


@dataclass
class RobustnessMetrics:
    """In-Sample vs Out-of-Sample split and Monte Carlo permutation metrics."""
    is_trade_count: int
    is_cagr: float
    is_max_drawdown: float
    is_sharpe: float
    is_insufficient_sample: bool
    oos_trade_count: int
    oos_cagr: float
    oos_max_drawdown: float
    oos_sharpe: float
    oos_insufficient_sample: bool
    degradation_ratio: float  # oos_cagr / is_cagr
    mc_p95_max_drawdown: float = 0.0  # 95th percentile worst drawdown in 1,000 permutations
    delta_cagr_pp: float = 0.0  # Raw percentage point difference (oos_cagr - is_cagr)
    cagr_ci_lower: float = 0.0  # 95% bootstrap lower bound on CAGR
    cagr_ci_upper: float = 0.0  # 95% bootstrap upper bound on CAGR
    is_directional_only: bool = False  # Flagged True when total trades < 30

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_trade_count": self.is_trade_count,
            "is_cagr": round(self.is_cagr, 4),
            "is_max_drawdown": round(self.is_max_drawdown, 4),
            "is_sharpe": round(self.is_sharpe, 4),
            "is_insufficient_sample": self.is_insufficient_sample,
            "oos_trade_count": self.oos_trade_count,
            "oos_cagr": round(self.oos_cagr, 4),
            "oos_max_drawdown": round(self.oos_max_drawdown, 4),
            "oos_sharpe": round(self.oos_sharpe, 4),
            "oos_insufficient_sample": self.oos_insufficient_sample,
            "degradation_ratio": round(self.degradation_ratio, 4),
            "delta_cagr_pp": round(self.delta_cagr_pp, 4),
            "mc_p95_max_drawdown": round(self.mc_p95_max_drawdown, 4),
            "cagr_ci_lower": round(self.cagr_ci_lower, 4),
            "cagr_ci_upper": round(self.cagr_ci_upper, 4),
            "is_directional_only": self.is_directional_only,
        }


@dataclass
class BacktestResult:
    """Complete output bundle for an index backtest run."""
    country: str
    index_name: str
    data_source_id: str
    currency: str
    provenance: DataProvenance
    data_start: str
    data_end: str
    trades: List[Trade]
    equity_curve: pd.DataFrame
    gross_metrics: PerformanceMetrics
    net_tax_metrics: Optional[PerformanceMetrics] = None
    net_discount_metrics: Optional[PerformanceMetrics] = None
    net_full_service_metrics: Optional[PerformanceMetrics] = None
    benchmark_discount_metrics: Optional[PerformanceMetrics] = None
    robustness: Optional[RobustnessMetrics] = None
    exclusion_reason: Optional[str] = None
