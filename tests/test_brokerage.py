"""Unit tests for Module D: Brokerage Adjustment Layer."""

import pytest
import pandas as pd
from src.engine.models import Trade
from src.brokerage.brokerage_calculator import BrokerageCalculator


def test_us_brokerage_point_in_time_transition(real_broker_calc):
    """Test US discount brokerage transition: $8.95 -> $4.95 -> $0.00 zero-commission."""
    # 2015: $8.95 fee
    fee_2015 = real_broker_calc.calculate_leg_fee(
        country="United States",
        broker_type="discount",
        trade_date=pd.Timestamp("2015-06-01"),
        trade_value=10000.0,
    )
    # 8.95 + 10000 * 0.00002 (SEC fee) = 8.95 + 0.20 = 9.15
    assert fee_2015 == pytest.approx(8.95 + 10000.0 * 0.00002, 0.05)

    # 2018: $4.95 fee
    fee_2018 = real_broker_calc.calculate_leg_fee(
        country="United States",
        broker_type="discount",
        trade_date=pd.Timestamp("2018-06-01"),
        trade_value=10000.0,
    )
    assert fee_2018 == pytest.approx(4.95 + 10000.0 * 0.00002, 0.05)

    # 2022: $0.00 zero commission
    fee_2022 = real_broker_calc.calculate_leg_fee(
        country="United States",
        broker_type="discount",
        trade_date=pd.Timestamp("2022-06-01"),
        trade_value=10000.0,
    )
    # Only SEC fee remains
    assert fee_2022 == pytest.approx(10000.0 * 0.00002, 0.05)


def test_full_service_brokerage_min_fee(real_broker_calc):
    """Test full-service min fee clamping (Morgan Stanley $50 min)."""
    # Small trade of $1,000: 0.35% is $3.50, clamped to min $50.00
    fee_small = real_broker_calc.calculate_leg_fee(
        country="United States",
        broker_type="full_service",
        trade_date=pd.Timestamp("2022-06-01"),
        trade_value=1000.0,
    )
    assert fee_small >= 50.0


def test_gst_and_stamp_duty_india(real_broker_calc):
    """Test Zerodha fee calculation in India including 18% GST and 0.1% STT."""
    trade_val = 100000.0  # 1 Lakh INR
    # Zerodha discount: flat 20 or 0.03% (0.03% of 100k is 30 -> capped at 20 INR)
    # GST on fee: 18% of 20 = 3.60 INR
    # Other charges (STT): 0.1% of 100,000 = 100.00 INR
    # Total = 20 + 3.60 + 100 = 123.60 INR
    fee = real_broker_calc.calculate_leg_fee(
        country="India",
        broker_type="discount",
        trade_date=pd.Timestamp("2023-01-01"),
        trade_value=trade_val,
    )
    assert fee == pytest.approx(123.60, 0.5)
