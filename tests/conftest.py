"""Pytest fixtures and configuration."""

import pytest
import pandas as pd
from pathlib import Path

from tests.synthetic import generate_synthetic_ohlcv
from src.tax.tax_calculator import TaxCalculator
from src.brokerage.brokerage_calculator import BrokerageCalculator


@pytest.fixture
def synthetic_bars() -> pd.DataFrame:
    """Generate 15 years of synthetic daily OHLCV bars (2011 to 2025)."""
    return generate_synthetic_ohlcv(
        start_date="2011-01-01",
        end_date="2025-12-31",
        start_price=1000.0,
        annual_drift=0.08,
        annual_vol=0.16,
        seed=42,
        regime="trend_and_cycle",
    )


@pytest.fixture
def root_dir() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture
def tax_dataset_path(root_dir) -> Path:
    return root_dir / "tax_dataset.csv"


@pytest.fixture
def brokerage_dataset_path(root_dir) -> Path:
    return root_dir / "brokerage_dataset.csv"


@pytest.fixture
def universe_path(root_dir) -> Path:
    return root_dir / "universe.yaml"


@pytest.fixture
def real_tax_calc(tax_dataset_path) -> TaxCalculator:
    return TaxCalculator(tax_dataset_path)


@pytest.fixture
def real_broker_calc(brokerage_dataset_path) -> BrokerageCalculator:
    return BrokerageCalculator(brokerage_dataset_path)
