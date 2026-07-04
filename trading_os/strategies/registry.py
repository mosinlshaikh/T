from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from trading_os.ai.decision_types import (
    DecisionAction,
    EvidenceItem,
    EvidenceType,
    SignalAssessment,
)


class StrategyName(str, Enum):
    WHALE_CONFIRMATION_STRATEGY = "WHALE_CONFIRMATION_STRATEGY"
    CANDLE_STRUCTURE_STRATEGY = "CANDLE_STRUCTURE_STRATEGY"
    NEWS_RISK_FILTER_STRATEGY = "NEWS_RISK_FILTER_STRATEGY"
    ORDER_BOOK_LIQUIDITY_STRATEGY = "ORDER_BOOK_LIQUIDITY_STRATEGY"
    MULTI_FACTOR_AI_STRATEGY = "MULTI_FACTOR_AI_STRATEGY"


class Strategy(Protocol):
    name: StrategyName

    def evaluate(self, symbol: str, evidence: list[EvidenceItem]) -> SignalAssessment | None: ...


@dataclass
class EvidenceRequiredStrategy:
    name: StrategyName
    required_evidence: set[EvidenceType]
    default_direction: DecisionAction = DecisionAction.SKIP
    minimum_confidence: float = 0.5

    def evaluate(self, symbol: str, evidence: list[EvidenceItem]) -> SignalAssessment | None:
        matched = [item for item in evidence if item.evidence_type in self.required_evidence]
        if len({item.evidence_type for item in matched}) < len(self.required_evidence):
            return None

        confidence = min(sum(item.confidence for item in matched) / len(matched), 1.0)
        if confidence < self.minimum_confidence:
            return SignalAssessment(
                name=f"{self.name.value}:{symbol.upper()}",
                direction=DecisionAction.SKIP,
                confidence=round(confidence, 4),
                source=self.name.value,
                evidence=matched,
            )
        return SignalAssessment(
            name=f"{self.name.value}:{symbol.upper()}",
            direction=self.default_direction,
            confidence=round(confidence, 4),
            source=self.name.value,
            evidence=matched,
        )


@dataclass
class StrategyRegistry:
    strategies: dict[StrategyName, Strategy] = field(default_factory=dict)

    @classmethod
    def with_default_placeholders(cls) -> "StrategyRegistry":
        registry = cls()
        registry.register(
            EvidenceRequiredStrategy(
                StrategyName.WHALE_CONFIRMATION_STRATEGY,
                {EvidenceType.WHALE_SIGNAL},
                DecisionAction.HOLD,
            )
        )
        registry.register(
            EvidenceRequiredStrategy(
                StrategyName.CANDLE_STRUCTURE_STRATEGY,
                {EvidenceType.CANDLE},
                DecisionAction.HOLD,
            )
        )
        registry.register(
            EvidenceRequiredStrategy(
                StrategyName.NEWS_RISK_FILTER_STRATEGY,
                {EvidenceType.NEWS_SIGNAL},
                DecisionAction.HOLD,
            )
        )
        registry.register(
            EvidenceRequiredStrategy(
                StrategyName.ORDER_BOOK_LIQUIDITY_STRATEGY,
                {EvidenceType.ORDER_BOOK},
                DecisionAction.HOLD,
            )
        )
        registry.register(
            EvidenceRequiredStrategy(
                StrategyName.MULTI_FACTOR_AI_STRATEGY,
                {EvidenceType.MARKET_TICK, EvidenceType.RISK_CHECK, EvidenceType.CAPITAL_CHECK},
                DecisionAction.HOLD,
            )
        )
        return registry

    def register(self, strategy: Strategy) -> None:
        self.strategies[strategy.name] = strategy

    def evaluate_all(self, symbol: str, evidence: list[EvidenceItem]) -> list[SignalAssessment]:
        signals: list[SignalAssessment] = []
        for strategy in self.strategies.values():
            signal = strategy.evaluate(symbol, evidence)
            if signal is not None:
                signals.append(signal)
        return signals
