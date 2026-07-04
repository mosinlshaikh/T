from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import EvidenceItem, EvidenceType


@dataclass
class WhaleIntelligenceEngine:
    watched_wallets: list[str] = field(default_factory=list)

    def evidence_from_observation(
        self, symbol: str, summary: str, confidence: float
    ) -> EvidenceItem:
        return EvidenceItem(
            evidence_type=EvidenceType.WHALE_SIGNAL,
            source="whale_intelligence",
            summary=f"{symbol.upper()}: {summary}",
            confidence=confidence,
        )
