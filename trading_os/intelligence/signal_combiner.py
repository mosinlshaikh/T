from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, SignalAssessment
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class CombinedSignal:
    symbol: str
    timeframe: Timeframe
    bullish_score: float
    bearish_score: float
    risk_score: float
    confidence_score: float
    conflicts: list[str]
    missing_data: list[str]
    final_signal: DecisionAction
    evidence: list[EvidenceItem] = field(default_factory=list)
    reason: str = ""

    def to_signal_assessment(self) -> SignalAssessment:
        return SignalAssessment(
            name="multi_factor_signal_combiner",
            direction=self.final_signal,
            confidence=self.confidence_score,
            source="multi_factor_signal_combiner",
            evidence=self.evidence,
        )


@dataclass
class MultiFactorSignalCombiner:
    required_signal_names: set[str] = field(
        default_factory=lambda: {
            "candle_intelligence",
            "news_risk_intelligence",
            "order_book_intelligence",
            "market_structure",
            "whale_intelligence_v1",
        }
    )
    min_confidence: float = 0.65
    high_news_risk_threshold: float = 0.7
    strong_conflict_threshold: float = 0.35

    def combine(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        signals: list[IntelligenceSignal],
    ) -> CombinedSignal:
        tf = normalize_timeframe(timeframe)
        missing = self._missing_required(signals)
        evidence = [item for signal in signals for item in signal.evidence]
        bullish = sum(
            signal.confidence for signal in signals if signal.direction == DecisionAction.BUY
        )
        bearish = sum(
            signal.confidence for signal in signals if signal.direction == DecisionAction.SELL
        )
        risk = min(sum(signal.risk_score for signal in signals), 1.0)
        conflicts = self._conflicts(signals)
        confidence = self._confidence(signals)

        if missing:
            final = DecisionAction.SKIP
            reason = "Required market intelligence data missing."
        elif risk >= self.high_news_risk_threshold:
            final = DecisionAction.SKIP
            reason = "News or market risk is high."
        elif conflicts and abs(bullish - bearish) <= self.strong_conflict_threshold:
            final = DecisionAction.SKIP
            reason = "Signals conflict strongly."
        elif confidence < self.min_confidence:
            final = DecisionAction.SKIP
            reason = "Combined confidence below threshold."
        elif bullish > bearish:
            final = DecisionAction.BUY
            reason = "Combined evidence is net bullish."
        elif bearish > bullish:
            final = DecisionAction.SELL
            reason = "Combined evidence is net bearish."
        else:
            final = DecisionAction.HOLD
            reason = "Combined evidence is neutral."

        return CombinedSignal(
            symbol=symbol.upper(),
            timeframe=tf,
            bullish_score=round(bullish, 4),
            bearish_score=round(bearish, 4),
            risk_score=round(risk, 4),
            confidence_score=confidence,
            conflicts=conflicts,
            missing_data=missing,
            final_signal=final,
            evidence=evidence,
            reason=reason,
        )

    def _missing_required(self, signals: list[IntelligenceSignal]) -> list[str]:
        available = {signal.name for signal in signals if not signal.missing_data}
        missing = sorted(self.required_signal_names - available)
        for signal in signals:
            missing.extend(signal.missing_data)
        return sorted(set(missing))

    @staticmethod
    def _conflicts(signals: list[IntelligenceSignal]) -> list[str]:
        directions = {
            signal.direction
            for signal in signals
            if signal.direction in {DecisionAction.BUY, DecisionAction.SELL}
        }
        if len(directions) <= 1:
            return []
        return [f"{signal.name}:{signal.direction.value}" for signal in signals]

    @staticmethod
    def _confidence(signals: list[IntelligenceSignal]) -> float:
        confidence_signals = [
            signal for signal in signals if signal.direction != DecisionAction.SKIP
        ]
        if not confidence_signals:
            return 0.0
        return round(
            min(
                sum(signal.confidence for signal in confidence_signals) / len(confidence_signals),
                1.0,
            ),
            4,
        )
