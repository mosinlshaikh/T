from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from trading_os.market.timeframes import Timeframe


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    SKIP = "SKIP"


class EvidenceType(str, Enum):
    MARKET_TICK = "market_tick"
    MARKET_SNAPSHOT = "market_snapshot"
    CANDLE = "candle"
    ORDER_BOOK = "order_book"
    WHALE_SIGNAL = "whale_signal"
    NEWS_SIGNAL = "news_signal"
    RISK_CHECK = "risk_check"
    CAPITAL_CHECK = "capital_check"


@dataclass(frozen=True)
class EvidenceItem:
    evidence_type: EvidenceType
    source: str
    summary: str
    confidence: float
    timestamp: str = field(default_factory=utc_now)
    payload: dict[str, object] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return bool(
            self.source
            and self.timestamp
            and isinstance(self.timestamp, str)
            and self.summary
            and 0.0 <= self.confidence <= 1.0
        )


@dataclass(frozen=True)
class SignalAssessment:
    name: str
    direction: DecisionAction
    confidence: float
    source: str
    timestamp: str = field(default_factory=utc_now)
    evidence: list[EvidenceItem] = field(default_factory=list)

    def is_valid(self) -> bool:
        return bool(
            self.name
            and self.source
            and self.timestamp
            and isinstance(self.timestamp, str)
            and 0.0 <= self.confidence <= 1.0
        )


@dataclass(frozen=True)
class DecisionProposal:
    symbol: str
    timeframe: Timeframe
    action: DecisionAction
    confidence: float
    evidence: list[EvidenceItem]
    reason: str
    missing_data: list[str] = field(default_factory=list)
    conflict_signals: list[str] = field(default_factory=list)
    signals: list[SignalAssessment] = field(default_factory=list)
    timestamp: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class VerifiedDecision:
    symbol: str
    timeframe: Timeframe
    action: DecisionAction
    confidence: float
    evidence: list[EvidenceItem]
    reason: str
    missing_data: list[str]
    conflict_signals: list[str]
    verified_decision: bool
    rejection_reason: str = ""
    timestamp: str = field(default_factory=utc_now)

    @property
    def verified(self) -> bool:
        return self.verified_decision
