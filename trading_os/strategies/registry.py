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
class CandleStructureStrategy(EvidenceRequiredStrategy):
    def evaluate(self, symbol: str, evidence: list[EvidenceItem]) -> SignalAssessment | None:
        candle_evidence = [
            item
            for item in evidence
            if item.evidence_type == EvidenceType.CANDLE and item.source == "candle_intelligence"
        ]
        if not candle_evidence:
            return None
        confidence = min(
            sum(item.confidence for item in candle_evidence) / len(candle_evidence), 1.0
        )
        if confidence < self.minimum_confidence:
            return SignalAssessment(
                name=f"{self.name.value}:{symbol.upper()}",
                direction=DecisionAction.SKIP,
                confidence=round(confidence, 4),
                source=self.name.value,
                evidence=candle_evidence,
            )
        direction = self._direction(candle_evidence)
        return SignalAssessment(
            name=f"{self.name.value}:{symbol.upper()}",
            direction=direction,
            confidence=round(confidence, 4),
            source=self.name.value,
            evidence=candle_evidence,
        )

    @staticmethod
    def _direction(evidence: list[EvidenceItem]) -> DecisionAction:
        for item in evidence:
            trend = str(item.payload.get("trend", "")).lower()
            breakout = bool(item.payload.get("breakout", False))
            volume_confirmed = bool(item.payload.get("volume_confirmed", False))
            reversal = bool(item.payload.get("reversal", False))
            wick_rejection = bool(item.payload.get("wick_rejection", False))
            if reversal or wick_rejection:
                return DecisionAction.HOLD
            if trend == "uptrend" and (breakout or volume_confirmed or item.confidence >= 0.5):
                return DecisionAction.BUY
            if trend == "downtrend" and (breakout or volume_confirmed or item.confidence >= 0.5):
                return DecisionAction.SELL
        return DecisionAction.HOLD


@dataclass
class OrderBookLiquidityStrategy(EvidenceRequiredStrategy):
    imbalance_signal_threshold: float = 0.18

    def evaluate(self, symbol: str, evidence: list[EvidenceItem]) -> SignalAssessment | None:
        signal = super().evaluate(symbol, evidence)
        if signal is None or signal.direction == DecisionAction.SKIP:
            return signal
        order_book_evidence = [
            item for item in signal.evidence if item.evidence_type == EvidenceType.ORDER_BOOK
        ]
        direction = self._direction(order_book_evidence)
        return SignalAssessment(
            name=signal.name,
            direction=direction,
            confidence=signal.confidence,
            source=signal.source,
            evidence=signal.evidence,
        )

    def _direction(self, evidence: list[EvidenceItem]) -> DecisionAction:
        for item in evidence:
            spread_risk = bool(item.payload.get("spread_risk", False))
            fake_wall = bool(item.payload.get("fake_wall_suspicion", False))
            buy_wall = bool(item.payload.get("buy_wall", False))
            sell_wall = bool(item.payload.get("sell_wall", False))
            imbalance = float(item.payload.get("bid_ask_imbalance", 0.0))
            if spread_risk or fake_wall:
                return DecisionAction.HOLD
            if buy_wall and not sell_wall:
                return DecisionAction.BUY
            if sell_wall and not buy_wall:
                return DecisionAction.SELL
            if imbalance >= self.imbalance_signal_threshold:
                return DecisionAction.BUY
            if imbalance <= -self.imbalance_signal_threshold:
                return DecisionAction.SELL
        return DecisionAction.HOLD


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
            CandleStructureStrategy(
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
            OrderBookLiquidityStrategy(
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
