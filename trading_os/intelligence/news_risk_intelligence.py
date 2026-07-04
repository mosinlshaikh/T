from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class NewsItem:
    headline: str
    source: str
    timestamp: str
    url: str = ""

    def is_valid(self) -> bool:
        return bool(self.headline and self.source and self.timestamp)


@dataclass
class BinanceAnnouncementAdapter:
    source_name: str = "binance_announcements"

    def normalize(self, items: list[dict[str, str]]) -> list[NewsItem]:
        return [
            NewsItem(
                headline=item.get("headline", ""),
                source=item.get("source", self.source_name),
                timestamp=item.get("timestamp", ""),
                url=item.get("url", ""),
            )
            for item in items
        ]


@dataclass
class CryptoNewsAdapter:
    source_name: str = "crypto_news"

    def normalize(self, items: list[dict[str, str]]) -> list[NewsItem]:
        return [
            NewsItem(
                headline=item.get("headline", ""),
                source=item.get("source", self.source_name),
                timestamp=item.get("timestamp", ""),
                url=item.get("url", ""),
            )
            for item in items
        ]


@dataclass
class NewsRiskIntelligenceEngine:
    listing_terms: list[str] = field(default_factory=lambda: ["listing", "new listing"])
    delisting_terms: list[str] = field(default_factory=lambda: ["delisting", "remove trading"])
    regulatory_terms: list[str] = field(
        default_factory=lambda: ["sec", "ban", "lawsuit", "regulator"]
    )
    negative_terms: list[str] = field(
        default_factory=lambda: ["hack", "exploit", "insolvent", "emergency"]
    )

    def analyze(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        news_items: list[NewsItem] | None,
    ) -> IntelligenceSignal:
        tf = normalize_timeframe(timeframe)
        if not news_items:
            return IntelligenceSignal(
                name="news_risk_intelligence",
                symbol=symbol.upper(),
                timeframe=tf,
                direction=DecisionAction.SKIP,
                confidence=0.0,
                missing_data=["news_source"],
                reason="News source missing; no news claim generated.",
            )

        valid = [item for item in news_items if item.is_valid()]
        if not valid:
            return IntelligenceSignal(
                name="news_risk_intelligence",
                symbol=symbol.upper(),
                timeframe=tf,
                direction=DecisionAction.SKIP,
                confidence=0.0,
                missing_data=["news_source_timestamp"],
                reason="News evidence missing source or timestamp.",
            )

        text = " ".join(item.headline.lower() for item in valid)
        listing = any(term in text for term in self.listing_terms)
        delisting = any(term in text for term in self.delisting_terms)
        regulatory = any(term in text for term in self.regulatory_terms)
        negative = any(term in text for term in self.negative_terms)
        risk_score = 0.0
        risk_score += 0.3 if delisting else 0.0
        risk_score += 0.3 if regulatory else 0.0
        risk_score += 0.4 if negative else 0.0
        direction = DecisionAction.HOLD if risk_score else DecisionAction.SKIP
        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.NEWS_SIGNAL,
                source="news_risk_intelligence",
                summary=(
                    f"listing={listing}; delisting={delisting}; regulatory={regulatory}; "
                    f"negative_emergency={negative}"
                ),
                confidence=round(min(max(risk_score, 0.25), 1.0), 4),
                timestamp=valid[-1].timestamp,
                payload={
                    "listing_risk_flag": listing,
                    "delisting_risk_flag": delisting,
                    "regulatory_risk_flag": regulatory,
                    "negative_sentiment_emergency_flag": negative,
                    "source_count": len(valid),
                },
            )
        ]
        return IntelligenceSignal(
            name="news_risk_intelligence",
            symbol=symbol.upper(),
            timeframe=tf,
            direction=direction,
            confidence=evidence[0].confidence,
            evidence=evidence,
            reason="News risk analysis completed with source/timestamp evidence.",
            risk_score=round(risk_score, 4),
        )
