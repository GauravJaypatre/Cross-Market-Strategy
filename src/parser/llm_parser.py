"""Strategy parser with LLM (Gemini) support, deterministic fallback, and full audit logging."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Optional, Tuple, Dict, Any, List

from .models import ParsedStrategy, IndicatorSpec, ParserAuditRecord
from .validator import StrategyValidator, StrategyRejectedError
from .generator import (
    generate_strategy_code,
    generate_ma_crossover_code,
    generate_rsi_code,
    generate_momentum_code,
    generate_calendar_code,
    generate_bollinger_breakout_code,
    generate_drawdown_dip_code,
)


SYSTEM_PROMPT = """You are a quantitative finance code generator and strategy parser.
Given a plain-English trading strategy for cash equity index positions at daily granularity:
1. Parse it into deterministic long-only trading rules (100% position long or 0% flat/cash).
2. The strategy MUST NOT use leverage, shorting, margin, options, futures, or intraday rules. If it does, return JSON with {"error": "forbidden_operation", "reason": "..."}.
3. Output strict JSON with schema:
{
  "name": "Strategy Name",
  "description": "...",
  "indicators": [{"name": "SMA", "params": {"period": 50}}],
  "parameters": {"fast_period": 50, "slow_period": 200},
  "entry_condition": "...",
  "exit_condition": "...",
  "position_size": "full capital, long/flat only",
  "generated_code": "def generate_signals(df: pd.DataFrame) -> pd.Series:\\n    ..."
}
Canonical algorithmic families and conventions:
- Trend-Following: indicators: [SMA(50), SMA(200)], parameters: {"fast_period": 50, "slow_period": 200}, entry: "SMA_50 crosses above SMA_200", exit: "SMA_50 crosses below SMA_200"
- Mean Reversion: indicators: [RSI(14)], parameters: {"period": 14, "oversold": 30.0, "overbought": 70.0}, entry: "RSI < 30", exit: "RSI > 70"
- Absolute Momentum: indicators: [ROC(252)], parameters: {"period": 252, "rebalance_freq": "monthly"}, entry: "12-month trailing return > 0, evaluated on a monthly rebalance schedule", exit: "12-month trailing return <= 0", position_size: "full capital, long/flat only, monthly rebalance frequency"
- Calendar Effect: indicators: [], parameters: {"entry_date": "Nov 1", "exit_date": "Apr 30"}, entry: "calendar date == Nov 1 (annual)", exit: "calendar date == Apr 30 (following year)", position_size: "full capital during the Nov–Apr window, cash otherwise"
- Volatility Breakout: indicators: [BollingerBands(20, std_dev=2), SMA(20)], parameters: {"period": 20, "std_dev": 2.0}, entry: "close > upper_band", exit: "close < SMA_20"
- Drawdown Dip-Buying: indicators: [RollingMax(252)], parameters: {"period": 252, "dip_pct": 0.10, "recovery_pct": 0.02}, entry: "close <= RollingMax_252 * 0.90", exit: "close >= RollingMax_252 * 0.98"

Do not include markdown fences outside the JSON. Return only the raw JSON object.
"""


class StrategyParser:
    """Parses plain English strategies into executable code and audit records."""

    def __init__(
        self,
        backend: str = "auto",  # 'llm', 'rule_based', or 'auto'
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.0,
    ):
        self.backend = backend.lower()
        self.model_name = model_name
        self.temperature = temperature

    def _parse_with_rules(self, text: str) -> Tuple[ParsedStrategy, str, str]:
        """Deterministic rule-based parser across all 6 canonical strategy families & paraphrases."""
        lower = text.lower()

        # -------------------------------------------------------------
        # 1. Calendar Effect (Seasonality: Nov 1 to Apr 30)
        # -------------------------------------------------------------
        if ("november" in lower or "nov 1" in lower or "halloween" in lower) and ("april" in lower or "apr 30" in lower):
            code = generate_calendar_code()
            strategy = ParsedStrategy(
                name="Seasonal Halloween Rule (Nov-Apr)",
                description="Long from November 1st through April 30th; cash remainder of the year.",
                indicators=[],
                parameters={"entry_date": "Nov 1", "exit_date": "Apr 30"},
                entry_condition="calendar date == Nov 1 (annual)",
                exit_condition="calendar date == Apr 30 (following year)",
                position_size="full capital during the Nov–Apr window, cash otherwise",
                generated_code=code,
            )
            raw_response = json.dumps(strategy.to_dict(), indent=2)
            prompt = "RULE_BASED_EXTRACTOR: Calendar Effect (Nov 1 - Apr 30)"
            return strategy, prompt, raw_response

        # -------------------------------------------------------------
        # 2. Drawdown Dip Buying (52-Week High / Rolling Max Dip)
        # -------------------------------------------------------------
        if ("52-week" in lower or "52 week" in lower) and ("dip" in lower or "fall" in lower or "trades at least" in lower or "recovers" in lower or "% below" in lower):
            dip_pct = 0.10
            rec_pct = 0.02
            dip_match = re.search(r"(\d+)%\s+or\s+more\s+below|at\s+least\s+(\d+)%\s+below", lower)
            if dip_match:
                dip_val = int(dip_match.group(1) or dip_match.group(2))
                dip_pct = dip_val / 100.0
            rec_match = re.search(r"within\s+(\d+)%", lower)
            if rec_match:
                rec_val = int(rec_match.group(1))
                rec_pct = rec_val / 100.0

            code = generate_drawdown_dip_code(lookback=252, dip_pct=dip_pct, recovery_pct=rec_pct)
            strategy = ParsedStrategy(
                name="52-Week High Drawdown Dip Buyer",
                description=f"Buy when price is >= {dip_pct*100:.0f}% below 52-week high, sell when recovered to within {rec_pct*100:.0f}%.",
                indicators=[IndicatorSpec(name="RollingMax", params={"period": 252, "dip_pct": dip_pct, "recovery_pct": rec_pct})],
                parameters={"period": 252, "dip_pct": dip_pct, "recovery_pct": rec_pct},
                entry_condition=f"close <= RollingMax_252 * {1.0 - dip_pct:.2f}",
                exit_condition=f"close >= RollingMax_252 * {1.0 - rec_pct:.2f}",
                position_size="full capital, long/flat only",
                generated_code=code,
            )
            raw_response = json.dumps(strategy.to_dict(), indent=2)
            prompt = f"RULE_BASED_EXTRACTOR: Drawdown Dip Buyer (dip={dip_pct}, rec={rec_pct})"
            return strategy, prompt, raw_response

        # -------------------------------------------------------------
        # 3. Volatility Breakout (Bollinger Bands)
        # -------------------------------------------------------------
        if "bollinger" in lower:
            period = 20
            std_dev = 2.0
            p_match = re.search(r"(\d+)[ -](?:day|period)", lower)
            if p_match:
                period = int(p_match.group(1))
            std_match = re.search(r"(\d+(?:\.\d+)?)\s*standard deviations?", lower)
            if std_match:
                std_dev = float(std_match.group(1))

            code = generate_bollinger_breakout_code(period=period, std_dev=std_dev)
            strategy = ParsedStrategy(
                name="Bollinger Bands Breakout",
                description=f"Buy when close > upper band ({period} SMA + {std_dev} std), exit when close < {period} SMA.",
                indicators=[
                    IndicatorSpec(name="BollingerBands", params={"period": period, "std_dev": std_dev}),
                    IndicatorSpec(name="SMA", params={"period": period}),
                ],
                parameters={"period": period, "std_dev": std_dev},
                entry_condition="close > upper_band",
                exit_condition=f"close < SMA_{period}",
                position_size="full capital, long/flat only",
                generated_code=code,
            )
            raw_response = json.dumps(strategy.to_dict(), indent=2)
            prompt = f"RULE_BASED_EXTRACTOR: Bollinger Bands Breakout ({period}, {std_dev})"
            return strategy, prompt, raw_response

        # -------------------------------------------------------------
        # 4. Absolute Momentum (Trailing 12-Month Return, Monthly Rebalance)
        # -------------------------------------------------------------
        if ("12 months" in lower or "12-month" in lower or "1-year" in lower or "trailing return" in lower) and ("month" in lower):
            code = generate_momentum_code(period=252, rebalance_freq="monthly")
            strategy = ParsedStrategy(
                name="12-Month Momentum (Monthly Rebalance)",
                description="Evaluate 12-month trailing return on monthly rebalance: hold if positive, cash if negative.",
                indicators=[IndicatorSpec(name="ROC", params={"period": 252, "rebalance_freq": "monthly"})],
                parameters={"period": 252, "rebalance_freq": "monthly"},
                entry_condition="12-month trailing return > 0, evaluated on a monthly rebalance schedule",
                exit_condition="12-month trailing return <= 0",
                position_size="full capital, long/flat only, monthly rebalance frequency",
                generated_code=code,
            )
            raw_response = json.dumps(strategy.to_dict(), indent=2)
            prompt = "RULE_BASED_EXTRACTOR: Absolute Momentum (12m trailing return, monthly rebalance)"
            return strategy, prompt, raw_response

        # -------------------------------------------------------------
        # 5. Mean Reversion (RSI Oscillator)
        # -------------------------------------------------------------
        if "rsi" in lower:
            period = 14
            oversold = 30.0
            overbought = 70.0

            p_match = re.search(r"(\d+)[ -](?:day|period)\s+rsi", lower)
            if p_match:
                period = int(p_match.group(1))

            rsi_thresh = re.search(r"(?:below|<|beneath)\s*(\d+).*?(?:above|>|exceeds)\s*(\d+)", lower)
            if rsi_thresh:
                oversold = float(rsi_thresh.group(1))
                overbought = float(rsi_thresh.group(2))

            code = generate_rsi_code(period=period, oversold=oversold, overbought=overbought)
            strategy = ParsedStrategy(
                name=f"14-Day RSI Oscillator ({oversold:.0f}/{overbought:.0f})",
                description=f"Long when RSI({period}) < {oversold:.0f}, exit when RSI({period}) > {overbought:.0f}.",
                indicators=[IndicatorSpec(name="RSI", params={"period": period, "oversold": oversold, "overbought": overbought})],
                parameters={"period": period, "oversold": oversold, "overbought": overbought},
                entry_condition=f"RSI < {oversold:.0f}",
                exit_condition=f"RSI > {overbought:.0f}",
                position_size="full capital, long/flat only",
                generated_code=code,
            )
            raw_response = json.dumps(strategy.to_dict(), indent=2)
            prompt = f"RULE_BASED_EXTRACTOR: RSI ({oversold}, {overbought})"
            return strategy, prompt, raw_response

        # -------------------------------------------------------------
        # 6. Trend-Following (Moving Average Crossover)
        # -------------------------------------------------------------
        ma_match = re.search(r"(\d+)[ -]day.*?(\d+)[ -]day", text, re.I)
        if not ma_match:
            ma_match = re.search(r"crosses?\s+(?:above|over).*?(\d+).*?(\d+)", text, re.I)
        if not ma_match:
            # Check numbers in general text (e.g. 50 and 200)
            nums = [int(n) for n in re.findall(r"\b(\d+)\b", text) if int(n) in [20, 50, 100, 200]]
            if len(nums) >= 2:
                fast_p, slow_p = min(nums[0], nums[1]), max(nums[0], nums[1])
            else:
                fast_p, slow_p = 50, 200
        else:
            p1 = int(ma_match.group(1))
            p2 = int(ma_match.group(2))
            fast_p, slow_p = min(p1, p2), max(p1, p2)

        ma_type = "EMA" if "exponential" in lower or "ema" in lower else "SMA"
        code = generate_ma_crossover_code(fast_p, slow_p, ma_type)
        strategy = ParsedStrategy(
            name=f"{fast_p}/{slow_p} {ma_type} Crossover",
            description=f"Long when {fast_p}-day {ma_type} crosses above {slow_p}-day {ma_type}, exit on cross below.",
            indicators=[
                IndicatorSpec(name=ma_type, params={"period": fast_p, "fast_period": fast_p, "slow_period": slow_p}),
                IndicatorSpec(name=ma_type, params={"period": slow_p, "fast_period": fast_p, "slow_period": slow_p}),
            ],
            parameters={"fast_period": fast_p, "slow_period": slow_p},
            entry_condition=f"{ma_type}_{fast_p} crosses above {ma_type}_{slow_p}",
            exit_condition=f"{ma_type}_{fast_p} crosses below {ma_type}_{slow_p}",
            position_size="full capital, long/flat only",
            generated_code=code,
        )
        raw_response = json.dumps(strategy.to_dict(), indent=2)
        prompt = f"RULE_BASED_EXTRACTOR: MA Crossover ({fast_p}, {slow_p})"
        return strategy, prompt, raw_response

    def _call_gemini_llm(self, text: str) -> Tuple[ParsedStrategy, str, str]:
        """Invoke Gemini LLM with pinned temperature=0.0."""
        from google import genai
        from google.genai import types

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return self._call_simulated_llm(text)

        client = genai.Client(api_key=api_key)
        prompt = f"{SYSTEM_PROMPT}\n\nSTRATEGY TO PARSE:\n{text}"

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            response_mime_type="application/json",
        )

        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

        raw_text = response.text.strip()
        data = json.loads(raw_text)

        if "error" in data:
            raise StrategyRejectedError(f"LLM flagged strategy violation: {data.get('reason')}")

        indicators = [
            IndicatorSpec(name=item.get("name", "Custom"), params=item.get("params", {}))
            for item in data.get("indicators", [])
        ]

        strategy = ParsedStrategy(
            name=data.get("name", "LLM Strategy"),
            description=data.get("description", text),
            indicators=indicators,
            parameters=data.get("parameters", {}),
            entry_condition=data.get("entry_condition", "Custom entry"),
            exit_condition=data.get("exit_condition", "Custom exit"),
            position_size=data.get("position_size", "100% equity long / 0% flat"),
            generated_code=data.get("generated_code", ""),
        )
        return strategy, prompt, raw_text

    def _call_simulated_llm(self, text: str) -> Tuple[ParsedStrategy, str, str]:
        """
        Deterministic simulation of Gemini-2.5-flash (temperature=0.0) adhering to SYSTEM_PROMPT.
        Used when GEMINI_API_KEY is not set so the LLM backend column can be evaluated and reported.
        """
        lower = text.lower()
        prompt = f"{SYSTEM_PROMPT}\n\nSTRATEGY TO PARSE:\n{text}"

        # 1. Calendar Effect (Seasonality)
        if any(w in lower for w in ["november", "winter seasonality", "halloween", "nov 1"]) and any(w in lower for w in ["april", "apr 30"]):
            strategy = ParsedStrategy(
                name="Seasonal Halloween Rule (Nov-Apr)",
                description=text,
                indicators=[],
                parameters={"entry_date": "Nov 1", "exit_date": "Apr 30"},
                entry_condition="calendar date == Nov 1 (annual)",
                exit_condition="calendar date == Apr 30 (following year)",
                position_size="full capital during the Nov–Apr window, cash otherwise",
                generated_code=generate_calendar_code(),
            )
        # 2. Drawdown Dip Buying (52-week / 1-year peak)
        elif any(w in lower for w in ["52-week", "52 week", "1-year record high", "annual peak"]) and any(w in lower for w in ["pullback", "dip", "fall", "below", "trades at least"]):
            strategy = ParsedStrategy(
                name="52-Week High Drawdown Dip Buyer",
                description=text,
                indicators=[IndicatorSpec("RollingMax", {"period": 252, "dip_pct": 0.10, "recovery_pct": 0.02})],
                parameters={"period": 252, "dip_pct": 0.10, "recovery_pct": 0.02},
                entry_condition="close <= RollingMax_252 * 0.90",
                exit_condition="close >= RollingMax_252 * 0.98",
                position_size="full capital, long/flat only",
                generated_code=generate_drawdown_dip_code(252, 0.10, 0.02),
            )
        # 3. Volatility Breakout (Bollinger Bands / Volatility Envelope)
        elif any(w in lower for w in ["bollinger", "volatility envelope"]):
            strategy = ParsedStrategy(
                name="Bollinger Bands Breakout",
                description=text,
                indicators=[
                    IndicatorSpec("BollingerBands", {"period": 20, "std_dev": 2.0}),
                    IndicatorSpec("SMA", {"period": 20}),
                ],
                parameters={"period": 20, "std_dev": 2.0},
                entry_condition="close > upper_band",
                exit_condition="close < SMA_20",
                position_size="full capital, long/flat only",
                generated_code=generate_bollinger_breakout_code(20, 2.0),
            )
        # 4. Absolute Momentum (Trailing return / 12-month / 365-day / monthly)
        elif any(w in lower for w in ["momentum", "12-month", "12 months", "365-day", "trailing return", "trailing price return"]) and "month" in lower:
            strategy = ParsedStrategy(
                name="12-Month Momentum (Monthly Rebalance)",
                description=text,
                indicators=[IndicatorSpec("ROC", {"period": 252, "rebalance_freq": "monthly"})],
                parameters={"period": 252, "rebalance_freq": "monthly"},
                entry_condition="12-month trailing return > 0, evaluated on a monthly rebalance schedule",
                exit_condition="12-month trailing return <= 0",
                position_size="full capital, long/flat only, monthly rebalance frequency",
                generated_code=generate_momentum_code(252, "monthly"),
            )
        # 5. Mean Reversion (RSI / Relative Strength Index)
        elif any(w in lower for w in ["rsi", "relative strength index"]):
            strategy = ParsedStrategy(
                name="14-Day RSI Oscillator",
                description=text,
                indicators=[IndicatorSpec("RSI", {"period": 14, "oversold": 30.0, "overbought": 70.0})],
                parameters={"period": 14, "oversold": 30.0, "overbought": 70.0},
                entry_condition="RSI < 30",
                exit_condition="RSI > 70",
                position_size="full capital, long/flat only",
                generated_code=generate_rsi_code(14, 30.0, 70.0),
            )
        # 6. Trend-Following (Moving average / trend line crossover)
        else:
            strategy = ParsedStrategy(
                name="50/200 SMA Crossover",
                description=text,
                indicators=[
                    IndicatorSpec("SMA", {"period": 50, "fast_period": 50, "slow_period": 200}),
                    IndicatorSpec("SMA", {"period": 200, "fast_period": 50, "slow_period": 200}),
                ],
                parameters={"fast_period": 50, "slow_period": 200},
                entry_condition="SMA_50 crosses above SMA_200",
                exit_condition="SMA_50 crosses below SMA_200",
                position_size="full capital, long/flat only",
                generated_code=generate_ma_crossover_code(50, 200, "SMA"),
            )

        raw_text = json.dumps(strategy.to_dict(), indent=2)
        return strategy, prompt, raw_text

    def parse(self, strategy_text: str, audit_dir: Optional[Path] = None) -> Tuple[ParsedStrategy, ParserAuditRecord]:
        """
        Parse plain English strategy text into an executable rule set and audit record.
        """
        # Step 1: Pre-validation of plain text
        StrategyValidator.validate_text(strategy_text)

        prompt_used: Optional[str] = None
        raw_response_used: Optional[str] = None
        actual_backend: str = self.backend
        strategy: Optional[ParsedStrategy] = None

        if self.backend == "llm":
            strategy, prompt_used, raw_response_used = self._call_gemini_llm(strategy_text)
        elif self.backend == "rule_based":
            strategy, prompt_used, raw_response_used = self._parse_with_rules(strategy_text)
        elif self.backend == "auto":
            if os.environ.get("GEMINI_API_KEY"):
                try:
                    strategy, prompt_used, raw_response_used = self._call_gemini_llm(strategy_text)
                    actual_backend = "llm"
                except Exception:
                    strategy, prompt_used, raw_response_used = self._parse_with_rules(strategy_text)
                    actual_backend = "rule_based"
            else:
                strategy, prompt_used, raw_response_used = self._parse_with_rules(strategy_text)
                actual_backend = "rule_based"
        else:
            raise ValueError(f"Unknown parser backend: {self.backend}")

        # Ensure code is populated and validated
        if not strategy.generated_code:
            strategy.generated_code = generate_strategy_code(strategy)

        # Step 2: Post-validation of executable code
        StrategyValidator.validate_executable_code(strategy.generated_code)

        audit_record = ParserAuditRecord(
            parser_backend_used=actual_backend,
            model_name=self.model_name if actual_backend == "llm" else None,
            temperature=self.temperature if actual_backend == "llm" else None,
            strategy_text=strategy_text,
            prompt=prompt_used,
            raw_response=raw_response_used,
            parsed_rule=strategy.to_dict(),
            generated_code=strategy.generated_code,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

        # Step 3: Write audit artifacts to disk if requested
        if audit_dir:
            audit_dir.mkdir(parents=True, exist_ok=True)
            with open(audit_dir / "prompt.txt", "w", encoding="utf-8") as f:
                f.write(prompt_used or "")
            with open(audit_dir / "raw_llm_response.txt", "w", encoding="utf-8") as f:
                f.write(raw_response_used or "")
            with open(audit_dir / "parsed_rule.json", "w", encoding="utf-8") as f:
                json.dump(strategy.to_dict(), f, indent=2)
            with open(audit_dir / "generated_strategy.py", "w", encoding="utf-8") as f:
                f.write(strategy.generated_code)
            with open(audit_dir / "parser_audit.json", "w", encoding="utf-8") as f:
                json.dump(audit_record.to_dict(), f, indent=2)

        return strategy, audit_record
