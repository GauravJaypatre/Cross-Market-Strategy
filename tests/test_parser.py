"""Unit tests for Module A: Strategy Parser."""

import json
from pathlib import Path
import pytest
import pandas as pd

from src.parser.models import ParsedStrategy
from src.parser.validator import StrategyValidator, StrategyRejectedError
from src.parser.llm_parser import StrategyParser
from tests.synthetic import generate_synthetic_ohlcv


def test_validator_rejects_forbidden_scopes():
    """Ensure all forbidden scope operations are strictly rejected."""
    forbidden_strategies = [
        ("Short the index when 50 MA crosses below 200 MA", "short"),
        ("Use 2x leverage to buy when RSI < 30", "leverage"),
        ("Buy on margin when price hits 20-day high", "margin"),
        ("Buy call options on breakout", "option"),
        ("Trade index futures using 5-minute bars", "future"),
        ("Enter on 15m intraday crossover", "intraday"),
    ]

    for strat_text, forbidden_word in forbidden_strategies:
        with pytest.raises(StrategyRejectedError) as exc_info:
            StrategyValidator.validate_text(strat_text)
        assert "Strategy rejected" in str(exc_info.value)


def test_validator_allows_negated_disclaimers():
    """Ensure explicit disclaimers like 'no shorting, no leverage' are NOT rejected."""
    allowed_text = (
        "Buy when the 50-day moving average crosses above the 200-day moving average, "
        "sell when it crosses below, using the full index value as position size, "
        "no leverage, no shorting, without options."
    )
    # Should not raise
    StrategyValidator.validate_text(allowed_text)


def test_rule_based_parser_ma_crossover(tmp_path):
    """Test deterministic rule-based parser on canonical 50/200 MA crossover."""
    parser = StrategyParser(backend="rule_based")
    strat_text = (
        "Buy when the 50-day moving average crosses above the 200-day moving average, "
        "sell when it crosses below, no leverage, no shorting."
    )
    audit_dir = tmp_path / "audit"
    strategy, audit = parser.parse(strat_text, audit_dir=audit_dir)

    assert strategy.name == "50/200 SMA Crossover"
    assert strategy.indicators[0].params["fast_period"] == 50
    assert strategy.indicators[0].params["slow_period"] == 200
    assert audit.parser_backend_used == "rule_based"

    # Verify audit files were created
    assert (audit_dir / "prompt.txt").exists()
    assert (audit_dir / "raw_llm_response.txt").exists()
    assert (audit_dir / "parsed_rule.json").exists()
    assert (audit_dir / "generated_strategy.py").exists()
    assert (audit_dir / "parser_audit.json").exists()


def test_generated_code_execution():
    """Test that generated strategy code executes cleanly and outputs valid {0, 1} series."""
    parser = StrategyParser(backend="rule_based")
    strategy, _ = parser.parse("Buy when 20-day MA crosses above 50-day MA, sell below")

    bars = generate_synthetic_ohlcv(start_date="2020-01-01", end_date="2022-12-31", seed=10)

    local_scope = {}
    exec(strategy.generated_code, {"pd": pd}, local_scope)
    generate_fn = local_scope["generate_signals"]

    signals = generate_fn(bars)
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(bars)
    assert set(signals.unique()).issubset({0, 1})
    # Should have triggered at least one trade
    assert (signals == 1).sum() > 0
