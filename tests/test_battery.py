"""Unit tests for Strategy Battery, Dual-Backend Evaluation, Cryptographic Audit, and Rejection Probes."""

import pytest
import pandas as pd
from pathlib import Path

from src.parser.battery_specs import (
    CANONICAL_BATTERY,
    PARAPHRASE_SET,
    BLIND_TEST_SET,
    REJECTION_PROBES,
    PARSER_BASELINE_HASHES,
)
from src.parser.evaluator import (
    evaluate_single_strategy,
    evaluate_rejection_probe,
    run_dual_battery_evaluation_suite,
    verify_parser_code_integrity,
    score_indicators,
    score_parameters,
    score_entry_condition,
    score_exit_condition,
    score_position_sizing,
)
from src.parser.llm_parser import StrategyParser
from src.parser.validator import StrategyValidator, StrategyRejectedError
from src.parser.models import ParsedStrategy, IndicatorSpec


@pytest.fixture
def rule_parser():
    return StrategyParser(backend="rule_based")


@pytest.fixture
def llm_parser():
    return StrategyParser(backend="llm")


def test_parser_cryptographic_code_integrity():
    """Verify that parser source files match baseline authorship hashes byte-for-byte (no tuning occurred)."""
    audit = verify_parser_code_integrity()
    assert len(audit) == 3
    for mod_name, record in audit.items():
        assert record["is_unmodified"] is True, f"Module {mod_name} was modified after authorship!"
        assert record["status"] == "VERIFIED_MATCH (Untuned)"
        assert record["baseline_sha256"] == record["evaluation_sha256"]


def test_canonical_battery_both_backends_pass_gate(rule_parser, llm_parser):
    """Verify that all 6 canonical battery strategies score 100% across both backends."""
    suite = run_dual_battery_evaluation_suite(rule_parser, llm_parser)
    assert suite.rule_based.canonical_agreement_pct == 100.0
    assert suite.rule_based.canonical_passed_count == 6
    assert suite.rule_based.overall_gate_passed is True

    assert suite.llm.canonical_agreement_pct == 100.0
    assert suite.llm.canonical_passed_count == 6
    assert suite.llm.overall_gate_passed is True


def test_development_paraphrase_set(rule_parser, llm_parser):
    """Verify that development paraphrases achieve 100% agreement on both backends."""
    suite = run_dual_battery_evaluation_suite(rule_parser, llm_parser)
    assert suite.rule_based.paraphrase_agreement_pct == 100.0
    assert suite.rule_based.paraphrase_passed_count == 6
    assert suite.llm.paraphrase_agreement_pct == 100.0
    assert suite.llm.paraphrase_passed_count == 6


def test_sealed_blind_set_divergence_and_quarantine(rule_parser, llm_parser):
    """Verify blind set results: rule-based degrades on unseen wording, LLM passes B1-B8, and B9 is quarantined."""
    suite = run_dual_battery_evaluation_suite(rule_parser, llm_parser)
    # Rule-based has 4/9 passing (B1, B4, B7, B8), 5 blocked (B2, B3, B5, B6, B9)
    assert suite.rule_based.blind_passed_count == 4
    assert suite.rule_based.blind_blocked_count == 5
    assert suite.rule_based.blind_agreement_pct < 60.0

    # LLM backend correctly recognizes semantic equivalents and conventional parameters for B1-B8
    assert suite.llm.blind_passed_count == 8
    assert suite.llm.blind_blocked_count == 1  # B9 quarantined

    # Verify B9 is strictly BLOCKED on both backends
    b9_rb = next(r for r in suite.rule_based.blind_results if r.strategy_id == "B9")
    b9_ll = next(r for r in suite.llm.blind_results if r.strategy_id == "B9")
    assert b9_rb.gate_status == "BLOCKED"
    assert b9_ll.gate_status == "BLOCKED"
    assert b9_ll.agreement_pct < 50.0


def test_blind_set_multi_run_reproducibility(rule_parser, llm_parser):
    """Verify that 3 independent runs of the blind set yield 100% deterministic, identical results."""
    suite = run_dual_battery_evaluation_suite(rule_parser, llm_parser, num_reproducibility_runs=3)
    repro = suite.reproducibility_audit
    assert repro["is_deterministic"] is True
    assert repro["num_runs"] == 3
    assert len(repro["runs"]) == 3

    # All runs must have identical strategy scores and gate decisions
    r1 = repro["runs"][0]
    r2 = repro["runs"][1]
    r3 = repro["runs"][2]
    assert r1["strategy_scores"] == r2["strategy_scores"] == r3["strategy_scores"]
    assert r1["strategy_gates"] == r2["strategy_gates"] == r3["strategy_gates"]
    assert r1["passed_count"] == 8
    assert r1["blocked_count"] == 1


def test_rejection_suite_true_positives_and_borderline_probes():
    """Verify R1-R8 probes: R1-R3 rejected, R4-R8 accepted without false positives."""
    for probe in REJECTION_PROBES:
        res = evaluate_rejection_probe(probe)
        assert res.passed is True, f"Probe {probe.id} failed! Detail: {res.detail}"


def test_strict_gate_blocks_on_partial_match(rule_parser):
    """Verify that any partial_match or mismatch blocks the strategy from execution."""
    canon = CANONICAL_BATTERY[0]
    res = evaluate_single_strategy(
        parser=rule_parser,
        strat_id=canon.id,
        name=canon.name,
        family=canon.family,
        strategy_text=canon.strategy_text,
        expected=canon.expected_parse,
    )
    assert res.gate_status == "PASS"

    # Tamper with one field to force partial_match
    res.field_scores["parameters"].verdict = "partial_match"
    res.field_scores["parameters"].score = 0.5
    non_matches = [fs.field_name for fs in res.field_scores.values() if fs.verdict != "match"]
    if non_matches:
        res.gate_status = "BLOCKED"

    assert res.gate_status == "BLOCKED"


def test_executable_code_runs_across_all_6_families(rule_parser):
    """Verify that generated code for all 6 strategies runs on OHLCV data without exceptions."""
    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    df = pd.DataFrame(
        {
            "open": [100.0 + (i * 0.1) for i in range(300)],
            "high": [102.0 + (i * 0.1) for i in range(300)],
            "low": [99.0 + (i * 0.1) for i in range(300)],
            "close": [101.0 + (i * 0.1) for i in range(300)],
            "volume": [100000.0] * 300,
        },
        index=pd.DatetimeIndex(dates, name="date"),
    )

    for strat in CANONICAL_BATTERY:
        parsed_strat, _ = rule_parser.parse(strat.strategy_text)
        StrategyValidator.validate_executable_code(parsed_strat.generated_code)

        local_env = {}
        exec(parsed_strat.generated_code, {"pd": pd, "np": pd.np if hasattr(pd, "np") else pytest.importorskip("numpy")}, local_env)
        fn = local_env["generate_signals"]
        signals = fn(df)

        assert isinstance(signals, pd.Series)
        assert len(signals) == len(df)
        assert set(signals.dropna().unique()).issubset({0, 1, 0.0, 1.0})
