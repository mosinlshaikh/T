from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DerivativesMode(str, Enum):
    RESEARCH_ONLY = "RESEARCH_ONLY"
    PAPER_ONLY = "PAPER_ONLY"
    LIVE_BLOCKED = "LIVE_BLOCKED"


class DerivativesInstrument(str, Enum):
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"


@dataclass(frozen=True)
class DerivativesReadiness:
    mode: DerivativesMode = DerivativesMode.RESEARCH_ONLY
    futures_execution_available: bool = False
    options_execution_available: bool = False
    leverage_execution_available: bool = False
    margin_required: bool = False
    live_trading_enabled: bool = False
    blocked_reasons: list[str] = field(default_factory=list)
    allowed_features: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DerivativesRiskEstimate:
    instrument: DerivativesInstrument
    symbol: str
    notional_usdt: float
    leverage: float
    margin_estimate_usdt: float
    adverse_move_pct: float
    estimated_loss_usdt: float
    liquidation_warning: str
    allowed_for_live_execution: bool = False
    mode: DerivativesMode = DerivativesMode.RESEARCH_ONLY
    safety_notes: list[str] = field(default_factory=list)
