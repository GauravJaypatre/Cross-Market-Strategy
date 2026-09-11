"""Strategy Battery specifications, gold standard targets, held-out paraphrases, and rejection probes."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExpectedParse:
    """Hand-annotated gold standard expected parse structure."""
    indicator_names: List[str]
    parameters: Dict[str, Any]
    entry_condition: str
    exit_condition: str
    position_sizing: str


@dataclass
class BatteryStrategy:
    """Canonical battery strategy item."""
    id: str
    family: str
    name: str
    strategy_text: str
    expected_parse: ExpectedParse
    rationale: str


@dataclass
class ParaphraseStrategy:
    """Held-out reworded variant for generalization testing."""
    id: str
    canonical_id: str
    name: str
    strategy_text: str
    expected_parse: ExpectedParse


@dataclass
class RejectionCase:
    """Validator test case for scope enforcement and false-positive avoidance."""
    id: str
    category: str  # 'leverage', 'shorting', 'derivatives', 'borderline_intent'
    strategy_text: str
    expected_rejected: bool
    rejection_reason_keyword: Optional[str]
    rationale: str


# =====================================================================
# 1. CANONICAL STRATEGY BATTERY (6 Distinct Algorithmic Families)
# =====================================================================

CANONICAL_BATTERY: List[BatteryStrategy] = [
    BatteryStrategy(
        id="S1",
        family="Trend-Following",
        name="50/200 SMA Crossover",
        strategy_text=(
            "Buy when the 50-day moving average crosses above the 200-day moving average, "
            "sell when it crosses below, using the full index value as position size, no leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["SMA", "SMA"],
            parameters={"fast_period": 50, "slow_period": 200},
            entry_condition="SMA_50 crosses above SMA_200",
            exit_condition="SMA_50 crosses below SMA_200",
            position_sizing="full capital, long/flat only",
        ),
        rationale="Baseline trend-following test measuring moving-average crossover detection and dual parameter extraction.",
    ),
    BatteryStrategy(
        id="S2",
        family="Mean Reversion",
        name="14-Day RSI Oscillator",
        strategy_text=(
            "Buy the index when the 14-day RSI drops below 30, and sell when the RSI rises back above 70. "
            "Hold the full position size, no shorting, no leverage."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["RSI"],
            parameters={"period": 14, "oversold": 30.0, "overbought": 70.0},
            entry_condition="RSI < 30",
            exit_condition="RSI > 70",
            position_sizing="full capital, long/flat only",
        ),
        rationale="Tests bounded oscillator handling (0-100 range) and specific non-default threshold extraction (30/70).",
    ),
    BatteryStrategy(
        id="S3",
        family="Absolute Momentum",
        name="12-Month Momentum (Monthly Rebalance)",
        strategy_text=(
            "At the start of each month, check the index's total return over the trailing 12 months. "
            "If it's positive, hold the index for the next month. If it's negative, stay in cash. "
            "No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["ROC"] if True else ["ROC"],  # or trailing 12-month return
            parameters={"period": 252, "rebalance_freq": "monthly"},
            entry_condition="12-month trailing return > 0, evaluated on a monthly rebalance schedule",
            exit_condition="12-month trailing return <= 0",
            position_sizing="full capital, long/flat only, monthly rebalance frequency",
        ),
        rationale="Tests extraction of non-daily rebalance frequency and trailing 12-month return lookback.",
    ),
    BatteryStrategy(
        id="S4",
        family="Calendar Effect",
        name="Seasonal Halloween Rule (Nov-Apr)",
        strategy_text=(
            "Buy the index on November 1st each year and sell on April 30th the following year. "
            "Stay in cash the rest of the time. No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=[],  # pure calendar rule, zero technical indicators
            parameters={"entry_date": "Nov 1", "exit_date": "Apr 30"},
            entry_condition="calendar date == Nov 1 (annual)",
            exit_condition="calendar date == Apr 30 (following year)",
            position_sizing="full capital during the Nov–Apr window, cash otherwise",
        ),
        rationale="Tests parser ability to handle strategies with zero technical indicators without hallucinating one.",
    ),
    BatteryStrategy(
        id="S5",
        family="Volatility Breakout",
        name="Bollinger Bands Breakout",
        strategy_text=(
            "Buy when the index closes above its upper Bollinger Band, using a 20-day moving average and 2 standard deviations. "
            "Sell when it closes back below the 20-day moving average. No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["BollingerBands", "SMA"],
            parameters={"period": 20, "std_dev": 2.0},
            entry_condition="close > upper_band",
            exit_condition="close < SMA_20",
            position_sizing="full capital, long/flat only",
        ),
        rationale="Tests multi-parameter compound indicator and entry/exit referencing different subcomponents of the same indicator.",
    ),
    BatteryStrategy(
        id="S6",
        family="Drawdown Dip-Buying",
        name="52-Week High Drawdown Dip Buyer",
        strategy_text=(
            "Buy the index whenever it falls 10% or more below its trailing 52-week high. "
            "Sell when it recovers to within 2% of that same 52-week high. No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["RollingMax"],
            parameters={"period": 252, "dip_pct": 0.10, "recovery_pct": 0.02},
            entry_condition="close <= RollingMax_252 * 0.90",
            exit_condition="close >= RollingMax_252 * 0.98",
            position_sizing="full capital, long/flat only",
        ),
        rationale="Tests relative-threshold condition anchored to rolling 52-week peak reference point rather than indicator crossover.",
    ),
]


# =====================================================================
# 2. HELD-OUT PARAPHRASE SET (Generalization Evaluation)
# =====================================================================

PARAPHRASE_SET: List[ParaphraseStrategy] = [
    ParaphraseStrategy(
        id="P1a",
        canonical_id="S1",
        name="Trend Crossover Paraphrase",
        strategy_text=(
            "Go long the index when the 50-day simple moving average crosses over the 200-day simple moving average; "
            "close the position when the 50-day falls back under the 200-day. Invest all available capital with no margin and no short sales."
        ),
        expected_parse=CANONICAL_BATTERY[0].expected_parse,
    ),
    ParaphraseStrategy(
        id="P2a",
        canonical_id="S2",
        name="RSI Mean Reversion Paraphrase",
        strategy_text=(
            "Enter a 100% long cash position when 14-period RSI drops beneath 30, and exit when the RSI indicator exceeds 70. "
            "Strictly avoid leverage or shorting."
        ),
        expected_parse=CANONICAL_BATTERY[1].expected_parse,
    ),
    ParaphraseStrategy(
        id="P3a",
        canonical_id="S3",
        name="Momentum Monthly Paraphrase",
        strategy_text=(
            "On the first trading day of each month, evaluate the 1-year (12-month) trailing price return. "
            "If the return is greater than zero, allocate 100% to the index for that month; otherwise hold 100% cash. "
            "No borrowed funds, no shorting."
        ),
        expected_parse=CANONICAL_BATTERY[2].expected_parse,
    ),
    ParaphraseStrategy(
        id="P4a",
        canonical_id="S4",
        name="Calendar Effect Paraphrase",
        strategy_text=(
            "Implement the seasonal Halloween effect: invest fully in the index starting November 1st and liquidate to cash on April 30th every year. "
            "No leverage, long only."
        ),
        expected_parse=CANONICAL_BATTERY[3].expected_parse,
    ),
    ParaphraseStrategy(
        id="P5a",
        canonical_id="S5",
        name="Bollinger Breakout Paraphrase",
        strategy_text=(
            "Buy when the daily close pierces above the upper Bollinger Band (20 periods, 2 standard deviations). "
            "Liquidate when the price crosses below the 20-day midline SMA. Long cash equity only, no leverage."
        ),
        expected_parse=CANONICAL_BATTERY[4].expected_parse,
    ),
    ParaphraseStrategy(
        id="P6a",
        canonical_id="S6",
        name="Drawdown Dip Paraphrase",
        strategy_text=(
            "Purchase the index whenever the closing price trades at least 10% below its 52-week peak. "
            "Sell the position once the price rallies back to within 2% of that 52-week peak. Cash equity only, no shorting, no leverage."
        ),
        expected_parse=CANONICAL_BATTERY[5].expected_parse,
    ),
]


# =====================================================================
# 3. SEALED BLIND SET (Never referenced during development; evaluated once)
# =====================================================================

BLIND_TEST_SET: List[ParaphraseStrategy] = [
    ParaphraseStrategy(
        id="B1",
        canonical_id="S1",
        name="Blind Trend Following (50/200 Trend Lines)",
        strategy_text=(
            "Maintain an equity position whenever the medium-term 50-bar simple trend line sits above the long-term 200-bar simple trend line, "
            "exiting when it drops underneath. Cash equity only, zero debt, zero shorting."
        ),
        expected_parse=CANONICAL_BATTERY[0].expected_parse,
    ),
    ParaphraseStrategy(
        id="B2",
        canonical_id="S2",
        name="Blind Mean Reversion (Welles Wilder RSI)",
        strategy_text=(
            "Capitalize on market oversold extremes by establishing long positions once Welles Wilder's Relative Strength Index (14 periods) "
            "registers lower than 30; unwind to cash when the oscillator travels beyond 70. Long only, no borrowing."
        ),
        expected_parse=CANONICAL_BATTERY[1].expected_parse,
    ),
    ParaphraseStrategy(
        id="B3",
        canonical_id="S3",
        name="Blind Momentum (Antonacci 365-Day Gain)",
        strategy_text=(
            "Execute a monthly Gary Antonacci dual-momentum filter: on the monthly opening session, measure the preceding 365-day cumulative gain; "
            "stay fully invested in the market if that trailing performance is above zero percent, else remain in cash. Long only."
        ),
        expected_parse=CANONICAL_BATTERY[2].expected_parse,
    ),
    ParaphraseStrategy(
        id="B4",
        canonical_id="S4",
        name="Blind Calendar Effect (Winter Seasonality)",
        strategy_text=(
            "Exploit winter seasonality: initiate full equity exposure on the opening day of November and close out the entire holding on the "
            "final day of April. Stay sidelined in cash from May through October. Long cash only, no margin."
        ),
        expected_parse=CANONICAL_BATTERY[3].expected_parse,
    ),
    ParaphraseStrategy(
        id="B5",
        canonical_id="S5",
        name="Blind Volatility Breakout (Volatility Envelope)",
        strategy_text=(
            "Enter a long trade when the daily bar settles past the upper volatility envelope calculated as a 20-day simple moving average "
            "plus two sample standard deviations. Exit as soon as the price falls beneath that same 20-day simple moving average. No margin or shorting."
        ),
        expected_parse=CANONICAL_BATTERY[4].expected_parse,
    ),
    ParaphraseStrategy(
        id="B6",
        canonical_id="S6",
        name="Blind Drawdown Dip-Buying (1-Year Peak Pullback)",
        strategy_text=(
            "Accumulate index shares when the price experiences a deep pullback of at least 10% from its 1-year record high. "
            "Liquidate when the market rebounds back to 98% of that annual peak. Cash equity, zero leverage."
        ),
        expected_parse=CANONICAL_BATTERY[5].expected_parse,
    ),
    ParaphraseStrategy(
        id="B7",
        canonical_id="S1",
        name="Blind Parameter-Missing Trend Following (Golden/Death Cross)",
        strategy_text=(
            "Buy the index on a golden cross of moving averages, and sell on a death cross. "
            "Full cash position, no shorting, no leverage."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["SMA", "SMA"],
            parameters={"fast_period": 50, "slow_period": 200},
            entry_condition="SMA_50 crosses above SMA_200",
            exit_condition="SMA_50 crosses below SMA_200",
            position_sizing="full capital, long/flat only",
        ),
    ),
    ParaphraseStrategy(
        id="B8",
        canonical_id="S2",
        name="Blind Parameter-Missing Mean Reversion (Oversold/Overbought RSI)",
        strategy_text=(
            "Buy when the market becomes oversold on the RSI, and sell when it becomes overbought. "
            "No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["RSI"],
            parameters={"period": 14, "oversold": 30.0, "overbought": 70.0},
            entry_condition="RSI < 30",
            exit_condition="RSI > 70",
            position_sizing="full capital, long/flat only",
        ),
    ),
    ParaphraseStrategy(
        id="B9",
        canonical_id="AMBIGUOUS",
        name="Blind Genuinely Underspecified Strategy (Qualitative Dip/Recovery)",
        strategy_text=(
            "Buy the index after significant market selloffs, and exit when the market recovers to normal levels. "
            "No leverage, no shorting."
        ),
        expected_parse=ExpectedParse(
            indicator_names=["UNDERSPECIFIED"],
            parameters={"underspecified": True},
            entry_condition="unspecified dip threshold (requires quantitative definition)",
            exit_condition="unspecified recovery threshold (requires quantitative definition)",
            position_sizing="full capital, long/flat only",
        ),
    ),
]


# =====================================================================
# CRYPTOGRAPHIC INTEGRITY BASELINE HASHES (Authorship-Time Checksums)
# =====================================================================

PARSER_BASELINE_HASHES: Dict[str, str] = {
    "llm_parser.py": "f74ebaa329166a963dded0b8ce8e7fb58518123f346dbc72169e71c612bdedc4",
    "generator.py": "2db932d58a20f74989674530235cd45121182603cb4050f7db1e545e2ad2799c",
    "validator.py": "36def7a77c846be3a32286a67f1ebb22f66e434dc748793ce5eb46fe4d3dcf41",
}


# =====================================================================
# 4. REJECTION & BORDERLINE INTENT PROBES (Validator Evaluation)
# =====================================================================

REJECTION_PROBES: List[RejectionCase] = [
    # True Positives (Must be rejected)
    RejectionCase(
        id="R1",
        category="leverage",
        strategy_text="Buy the index with 2x leverage when the 50-day MA crosses above the 200-day MA.",
        expected_rejected=True,
        rejection_reason_keyword="leverage",
        rationale="Active operational instruction to apply 2x leverage multiplier.",
    ),
    RejectionCase(
        id="R2",
        category="shorting",
        strategy_text="Short the index when RSI rises above 70, cover when it drops below 30.",
        expected_rejected=True,
        rejection_reason_keyword="short",
        rationale="Active operational instruction to open short positions.",
    ),
    RejectionCase(
        id="R3",
        category="derivatives",
        strategy_text="Buy call options on the index when the 50-day MA crosses above the 200-day MA.",
        expected_rejected=True,
        rejection_reason_keyword="derivative",
        rationale="Active operational instruction to trade derivative options.",
    ),
    # False Positive Probes (Must be ACCEPTED and parsed normally)
    RejectionCase(
        id="R4",
        category="borderline_intent",
        strategy_text="Avoid holding the index during periods of high leverage in the broader financial system; buy when the 50-day MA crosses above the 200-day MA.",
        expected_rejected=False,
        rejection_reason_keyword=None,
        rationale="'Leverage' appears descriptively referring to macroeconomic conditions, not an instruction to borrow.",
    ),
    RejectionCase(
        id="R5",
        category="borderline_intent",
        strategy_text="Hold the index for a short period of time after the 50-day MA crosses above the 200-day MA, then sell.",
        expected_rejected=False,
        rejection_reason_keyword=None,
        rationale="'Short' describes temporal duration/holding period, not short-selling.",
    ),
    RejectionCase(
        id="R6",
        category="borderline_intent",
        strategy_text="Investors have the option to buy the index when the 50-day MA crosses above the 200-day MA and exit when it crosses below.",
        expected_rejected=False,
        rejection_reason_keyword=None,
        rationale="'Option' is colloquial English for choice/discretion, not an options derivative contract.",
    ),
    RejectionCase(
        id="R7",
        category="borderline_intent",
        strategy_text="Anticipate positive future economic growth by buying when the 50-day MA crosses above the 200-day MA; exit on cross below.",
        expected_rejected=False,
        rejection_reason_keyword=None,
        rationale="'Future' refers to time horizon/economic outlook, not a futures derivative contract.",
    ),
    RejectionCase(
        id="R8",
        category="borderline_intent",
        strategy_text="Ensure a margin of safety by purchasing the index when 14-day RSI falls below 30, and sell when RSI exceeds 70.",
        expected_rejected=False,
        rejection_reason_keyword=None,
        rationale="'Margin of safety' is classic value investing terminology, not buying on margin.",
    ),
]
