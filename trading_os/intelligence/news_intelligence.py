from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import EvidenceItem, EvidenceType


@dataclass
class NewsIntelligenceEngine:
    sources: list[str] = field(default_factory=list)

    def evidence_from_headline(self, symbol: str, headline: str, confidence: float) -> EvidenceItem:
        return EvidenceItem(
            evidence_type=EvidenceType.NEWS_SIGNAL,
            source="news_intelligence",
            summary=f"{symbol.upper()}: {headline}",
            confidence=confidence,
        )
