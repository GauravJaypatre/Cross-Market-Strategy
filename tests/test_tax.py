"""Unit tests for Module C: Tax Adjustment Layer."""

import pytest
import pandas as pd
from src.engine.models import Trade
from src.tax.tax_calculator import TaxCalculator, apply_tax_adjustment


def test_point_in_time_tax_transition_india(real_tax_calc):
    """Test point-in-time tax rate transition for India across three regulatory regimes."""
    # Trade 1: Exit in 2017 (holding > 365 days -> 0% LTCG exempt)
    t_2017 = Trade(
        trade_id=1,
        entry_date=pd.Timestamp("2016-01-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2017-06-01"),
        exit_price=150.0,
        shares=1000.0,
        gross_pnl=50000.0,
        gross_return_pct=0.5,
        holding_period_days=517,
    )
    tax_2017 = real_tax_calc.calculate_trade_tax(t_2017, "India")
    # Section 10(38) LTCG was exempt pre-2018
    assert tax_2017 == 0.0

    # Trade 2: Exit in 2023 (holding > 365 days -> 10% LTCG above 100,000 INR exemption)
    t_2023 = Trade(
        trade_id=2,
        entry_date=pd.Timestamp("2021-01-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2023-01-01"),
        exit_price=250.0,
        shares=1000.0,
        gross_pnl=150000.0,  # 1.5 Lakhs
        gross_return_pct=1.5,
        holding_period_days=730,
    )
    tax_2023 = real_tax_calc.calculate_trade_tax(t_2023, "India")
    # Taxable = 150000 - 100000 = 50000; 10% of 50000 = 5000
    assert tax_2023 == pytest.approx(5000.0, 1.0)

    # Trade 3: Exit in August 2024 (Budget 2024: STCG 20%, LTCG 12.5% above 1.25L exemption)
    t_2024_short = Trade(
        trade_id=3,
        entry_date=pd.Timestamp("2024-05-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2024-08-15"),
        exit_price=120.0,
        shares=1000.0,
        gross_pnl=20000.0,
        gross_return_pct=0.2,
        holding_period_days=106,
    )
    tax_2024_short = real_tax_calc.calculate_trade_tax(t_2024_short, "India")
    # STCG is 20% on short term: 20% of 20000 = 4000
    assert tax_2024_short == pytest.approx(4000.0, 1.0)


def test_holding_period_dependent_us(real_tax_calc):
    """Test US holding period dependent rate (short-term vs long-term)."""
    # Short-term (< 365 days): 24% rate
    t_short = Trade(
        trade_id=1,
        entry_date=pd.Timestamp("2022-01-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2022-06-01"),
        exit_price=120.0,
        shares=100.0,
        gross_pnl=2000.0,
        gross_return_pct=0.2,
        holding_period_days=151,
    )
    tax_short = real_tax_calc.calculate_trade_tax(t_short, "United States")
    assert tax_short == pytest.approx(2000.0 * 0.24, 0.1)

    # Long-term (>= 365 days): 15% rate
    t_long = Trade(
        trade_id=2,
        entry_date=pd.Timestamp("2022-01-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2023-01-15"),
        exit_price=120.0,
        shares=100.0,
        gross_pnl=2000.0,
        gross_return_pct=0.2,
        holding_period_days=379,
    )
    tax_long = real_tax_calc.calculate_trade_tax(t_long, "United States")
    assert tax_long == pytest.approx(2000.0 * 0.15, 0.1)


def test_losses_are_not_taxed(real_tax_calc):
    """Ensure losing trades have exactly 0 tax."""
    t_loss = Trade(
        trade_id=1,
        entry_date=pd.Timestamp("2022-01-01"),
        entry_price=100.0,
        exit_date=pd.Timestamp("2022-06-01"),
        exit_price=80.0,
        shares=100.0,
        gross_pnl=-2000.0,
        gross_return_pct=-0.2,
        holding_period_days=151,
    )
    tax = real_tax_calc.calculate_trade_tax(t_loss, "United States")
    assert tax == 0.0
