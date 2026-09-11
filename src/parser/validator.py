"""Scope validator for trading strategies.

Enforces:
- Long-only cash equity positions
- 100% equity when long, 0% when flat
- No shorting
- No leverage or margin
- No derivatives (options, futures, swaps)
- Daily granularity only (no intraday)
"""

import re
from typing import List
import pandas as pd
import numpy as np


class StrategyRejectedError(Exception):
    """Raised when a strategy violates long-only cash equity scope."""
    pass


class StrategyValidator:
    """Validates plain English strategy descriptions and generated code."""

    FORBIDDEN_PATTERNS = [
        (r"\b(short|shorting|sell short|short position|short-selling)\b", "Shorting is strictly out of scope (long-only cash equity only)."),
        (r"\b(leverage|leveraged|margin|borrow|gearing|2x|3x|-2x|-3x)\b", "Leverage/margin is strictly out of scope."),
        (r"\b(option|options|put|call|straddle|strangle|future|futures|derivatives|swap|swaps|cfd|cfds|warrant)\b", "Derivatives are strictly out of scope."),
        (r"\b(intraday|tick|minute|minutes|\b1m\b|\b5m\b|\b15m\b|\b30m\b|\b1h\b|\b4h\b|hourly|day-trading)\b", "Intraday execution is strictly out of scope (daily bars only)."),
    ]

    @classmethod
    def validate_text(cls, text: str) -> None:
        """
        Scan strategy text for forbidden scope violations (leverage, shorting, derivatives, intraday).
        Employs intent-based detection to distinguish active operational instructions from
        negated disclaimers and descriptive market commentary.
        """
        clean_text = text.strip()
        lower_text = clean_text.lower()

        def is_negated(match_start: int) -> bool:
            lookback_window = lower_text[max(0, match_start - 35):match_start]
            negations = ["no ", "not ", "zero ", "without ", "avoid ", "strictly avoid ", "never "]
            return any(neg in lookback_window for neg in negations)

        # 1. Check for Leverage / Margin
        # 1a. Multiplier pattern (e.g. '2x', '3x', '-2x')
        mult_match = re.search(r"\b(-?\d+(?:\.\d+)?x)\b", clean_text, re.IGNORECASE)
        if mult_match and not is_negated(mult_match.start()):
            raise StrategyRejectedError(
                f"Strategy rejected: matches forbidden pattern '{mult_match.group(0)}'. Reason: Leverage/margin is strictly out of scope."
            )

        # 1b. Operational leverage / margin keywords
        lev_match = re.search(r"\b(leverage|leveraged|margin|gearing|borrowed funds)\b", clean_text, re.IGNORECASE)
        if lev_match and not is_negated(lev_match.start()):
            matched_word = lev_match.group(0).lower()
            start = lev_match.start()
            context_after = lower_text[start:start + 25]
            context_before = lower_text[max(0, start - 35):start]

            # False-positive guard: 'margin of safety' (value investing)
            if "margin of safety" in context_after:
                pass
            # False-positive guard: descriptive macroeconomic commentary
            elif any(desc in context_before for desc in ["periods of", "level of", "systemic", "macro", "financial system", "economy"]):
                pass
            else:
                raise StrategyRejectedError(
                    f"Strategy rejected: matches forbidden pattern '{matched_word}'. Reason: Leverage/margin is strictly out of scope."
                )

        # 2. Check for Shorting
        short_match = re.search(
            r"\b(short|shorting|sell short|short position|short-selling|open short|go short|cover)\b",
            clean_text,
            re.IGNORECASE,
        )
        if short_match and not is_negated(short_match.start()):
            start = short_match.start()
            context_after = lower_text[start:start + 25]
            # False-positive guard: temporal duration ('short period', 'short term', etc.)
            if any(term in context_after for term in ["short period", "short term", "short duration", "short timeframe", "short time"]):
                pass
            else:
                raise StrategyRejectedError(
                    f"Strategy rejected: matches forbidden pattern '{short_match.group(0)}'. Reason: Shorting is strictly out of scope (long-only cash equity only)."
                )

        # 3. Check for Derivatives
        deriv_match = re.search(
            r"\b(options?|calls?|puts?|futures?|derivatives?|swaps?|cfds?|warrants?|straddles?|strangles?)\b",
            clean_text,
            re.IGNORECASE,
        )
        if deriv_match and not is_negated(deriv_match.start()):
            start = deriv_match.start()
            context_after = lower_text[start:start + 30]
            context_before = lower_text[max(0, start - 25):start]

            # False-positive guard: colloquial option (choice/discretion)
            is_colloquial_option = "option to" in context_after or "have the option" in (context_before + context_after)
            # False-positive guard: temporal future (economic growth, market outlook)
            is_future_time = any(
                f in context_after for f in ["future economic", "future growth", "future outlook", "future performance", "future returns"]
            ) or "in the future" in (context_before + context_after) or "positive future" in context_before
            # False-positive guard: 'call' as verb (e.g. 'we call this')
            is_call_verb = ("call this" in context_after or "we call" in context_before) and "option" not in context_after

            if is_colloquial_option or is_future_time or is_call_verb:
                pass
            else:
                raise StrategyRejectedError(
                    f"Strategy rejected: matches forbidden pattern '{deriv_match.group(0)}'. Reason: Derivatives are strictly out of scope."
                )

        # 4. Check for Intraday
        intra_match = re.search(
            r"\b(intraday|tick|minute|minutes|\b1m\b|\b5m\b|\b15m\b|\b30m\b|\b1h\b|\b4h\b|hourly|day-trading)\b",
            clean_text,
            re.IGNORECASE,
        )
        if intra_match and not is_negated(intra_match.start()):
            raise StrategyRejectedError(
                f"Strategy rejected: matches forbidden pattern '{intra_match.group(0)}'. Reason: Intraday execution is strictly out of scope (daily bars only)."
            )

    @classmethod
    def validate_executable_code(cls, code: str) -> None:
        """
        Validate generated Python code by executing in sandboxed scope with dummy OHLCV.
        Must define generate_signals(df: pd.DataFrame) -> pd.Series.
        """
        # Forbidden calls in generated code
        for danger in ["import os", "import sys", "subprocess", "eval(", "exec(", "open(", "__import__"]:
            if danger in code:
                raise StrategyRejectedError(f"Generated code contains forbidden call: {danger}")

        local_namespace = {}
        try:
            exec(code, {"pd": pd, "np": np}, local_namespace)
        except Exception as e:
            raise StrategyRejectedError(f"Generated code failed compilation/syntax check: {e}")

        if "generate_signals" not in local_namespace:
            raise StrategyRejectedError("Generated code does not define required function 'generate_signals(df)'.")

        # Test against dummy dataframe
        dates = pd.date_range("2020-01-01", periods=10, freq="B")
        dummy_df = pd.DataFrame(
            {
                "open": [100.0 + i for i in range(10)],
                "high": [102.0 + i for i in range(10)],
                "low": [99.0 + i for i in range(10)],
                "close": [101.0 + i for i in range(10)],
                "volume": [1000.0] * 10,
            },
            index=pd.DatetimeIndex(dates, name="date"),
        )

        try:
            signals = local_namespace["generate_signals"](dummy_df)
        except Exception as e:
            raise StrategyRejectedError(f"generate_signals(dummy_df) raised exception: {e}")

        if not isinstance(signals, pd.Series):
            raise StrategyRejectedError(f"generate_signals must return pd.Series, got {type(signals)}.")

        if len(signals) != len(dummy_df):
            raise StrategyRejectedError(f"Signal series length ({len(signals)}) does not match input ({len(dummy_df)}).")

        # Ensure signal values are strictly in {0, 1}
        unique_vals = set(signals.dropna().unique())
        if not unique_vals.issubset({0, 1, 0.0, 1.0}):
            raise StrategyRejectedError(f"Signal values must be long (1) or flat (0) only. Found: {unique_vals}")
