from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import (
    DecisionAction,
    DecisionProposal,
    EvidenceItem,
    EvidenceType,
    SignalAssessment,
)
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass
class AIDecisionBrain:
    """AI decision-brain v1.

    This is deterministic and evidence-bound. It does not invent whale, news,
    candle, or profit claims. It produces only BUY, SELL, HOLD, or SKIP.
    """

    minimum_confidence: float = 0.65
    required_evidence: set[EvidenceType] = field(
        default_factory=lambda: {
            EvidenceType.MARKET_TICK,
            EvidenceType.RISK_CHECK,
            EvidenceType.CAPITAL_CHECK,
        }
    )

    def propose(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        evidence: list[EvidenceItem],
        signals: list[SignalAssessment],
    ) -> DecisionProposal:
        tf = normalize_timeframe(timeframe)
        missing_data = self._missing_evidence(evidence)

        if not evidence:
            return self._proposal(
                symbol,
                tf,
                DecisionAction.SKIP,
                0.0,
                evidence,
                "No evidence was provided.",
                missing_data or [item.value for item in self.required_evidence],
                [],
                signals,
            )

        if missing_data:
            return self._proposal(
                symbol,
                tf,
                DecisionAction.SKIP,
                0.0,
                evidence,
                "Required decision data is missing.",
                missing_data,
                [],
                signals,
            )

        if not signals:
            return self._proposal(
                symbol,
                tf,
                DecisionAction.SKIP,
                0.0,
                evidence,
                "No signal assessments were provided.",
                [],
                [],
                signals,
            )

        conflict_signals = self._conflict_signals(signals)
        decision_signals = [signal for signal in signals if signal.direction != DecisionAction.SKIP]
        confidence_signals = decision_signals or signals
        confidence = min(
            sum(signal.confidence for signal in confidence_signals) / len(confidence_signals),
            1.0,
        )

        if conflict_signals:
            return self._proposal(
                symbol,
                tf,
                DecisionAction.HOLD,
                round(confidence, 4),
                evidence,
                "Signals conflict; holding by policy.",
                [],
                conflict_signals,
                signals,
            )

        direction = self._dominant_direction(decision_signals)
        if confidence < self.minimum_confidence:
            action = DecisionAction.SKIP
            reason = "Signal confidence below threshold."
        elif direction in {DecisionAction.BUY, DecisionAction.SELL}:
            action = direction
            reason = "Decision proposal based on aligned evidence."
        else:
            action = DecisionAction.HOLD
            reason = "No actionable direction."

        return self._proposal(
            symbol,
            tf,
            action,
            round(confidence, 4),
            evidence,
            reason,
            [],
            [],
            signals,
        )

    def _missing_evidence(self, evidence: list[EvidenceItem]) -> list[str]:
        available = {item.evidence_type for item in evidence}
        return sorted(item.value for item in self.required_evidence - available)

    @staticmethod
    def _conflict_signals(signals: list[SignalAssessment]) -> list[str]:
        directions = {signal.direction for signal in signals}
        actionable_directions = directions & {DecisionAction.BUY, DecisionAction.SELL}
        if len(actionable_directions) <= 1:
            return []
        return [
            f"{signal.name}:{signal.direction.value}"
            for signal in signals
            if signal.direction in actionable_directions
        ]

    @staticmethod
    def _dominant_direction(signals: list[SignalAssessment]) -> DecisionAction:
        directions = {signal.direction for signal in signals}
        if DecisionAction.BUY in directions and DecisionAction.SELL not in directions:
            return DecisionAction.BUY
        if DecisionAction.SELL in directions and DecisionAction.BUY not in directions:
            return DecisionAction.SELL
        if DecisionAction.HOLD in directions:
            return DecisionAction.HOLD
        return DecisionAction.SKIP

    @staticmethod
    def _proposal(
        symbol: str,
        timeframe: Timeframe,
        action: DecisionAction,
        confidence: float,
        evidence: list[EvidenceItem],
        reason: str,
        missing_data: list[str],
        conflict_signals: list[str],
        signals: list[SignalAssessment],
    ) -> DecisionProposal:
        return DecisionProposal(
            symbol=symbol.upper(),
            timeframe=timeframe,
            action=action,
            confidence=confidence,
            evidence=evidence,
            reason=reason,
            missing_data=missing_data,
            conflict_signals=conflict_signals,
            signals=signals,
        )
