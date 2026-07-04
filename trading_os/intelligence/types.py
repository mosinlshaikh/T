from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from trading_os.ai.decision_types import DecisionAction, EvidenceItem
from trading_os.market.timeframes import Timeframe


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IntelligenceSignal:
    name: str
    symbol: str
    timeframe: Timeframe
    direction: DecisionAction
    confidence: float
    evidence: list[EvidenceItem] = field(default_factory=list)
    reason: str = ""
    missing_data: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    timestamp: str = field(default_factory=utc_now)

    @property
    def has_signal(self) -> bool:
        return (
            bool(self.evidence) and not self.missing_data and self.direction != DecisionAction.SKIP
        )
