"""Data schemas for parsed trading strategies and audit records."""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class IndicatorSpec:
    """Specification of an indicator used in strategy."""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedStrategy:
    """Deterministic, structured trading rule set."""
    name: str
    description: str
    indicators: List[IndicatorSpec]
    entry_condition: str
    exit_condition: str
    position_size: str = "100% equity long / 0% flat"
    parameters: Dict[str, Any] = field(default_factory=dict)
    no_leverage: bool = True
    no_shorting: bool = True
    generated_code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "indicators": [{"name": ind.name, "params": ind.params} for ind in self.indicators],
            "parameters": self.parameters,
            "entry_condition": self.entry_condition,
            "exit_condition": self.exit_condition,
            "position_size": self.position_size,
            "no_leverage": self.no_leverage,
            "no_shorting": self.no_shorting,
            "generated_code": self.generated_code,
        }


@dataclass
class ParserAuditRecord:
    """Full reproducibility log of strategy parsing."""
    parser_backend_used: str  # 'llm' or 'rule_based'
    model_name: Optional[str]
    temperature: Optional[float]
    strategy_text: str
    prompt: Optional[str]
    raw_response: Optional[str]
    parsed_rule: Dict[str, Any]
    generated_code: str
    timestamp_utc: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
