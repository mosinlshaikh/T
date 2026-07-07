from __future__ import annotations

from dataclasses import dataclass, field

from quality.hallucination_guard import detect_unsafe_claims
from trading_os.ai.decision_types import (
    DecisionAction,
    DecisionProposal,
    EvidenceItem,
    EvidenceType,
    VerifiedDecision,
)


@dataclass
class VerifiedDecisionEngine:
    """Zero-hallucination decision gate.

    Invariants:
    - no evidence -> SKIP
    - missing required data -> SKIP
    - invalid source/timestamp -> SKIP
    - conflicting signals -> HOLD
    - unsupported claims -> SKIP with rejection reason
    """

    required_evidence: set[EvidenceType] = field(
        default_factory=lambda: {
            EvidenceType.MARKET_TICK,
            EvidenceType.RISK_CHECK,
            EvidenceType.CAPITAL_CHECK,
        }
    )

    def verify(self, proposal: DecisionProposal) -> VerifiedDecision:
        if not proposal.evidence:
            return self._blocked(proposal, DecisionAction.SKIP, "Missing evidence.")

        invalid_evidence = [item for item in proposal.evidence if not item.is_valid()]
        if invalid_evidence:
            return self._blocked(
                proposal, DecisionAction.SKIP, "Evidence missing source/timestamp."
            )

        invalid_signals = [signal for signal in proposal.signals if not signal.is_valid()]
        if invalid_signals:
            return self._blocked(proposal, DecisionAction.SKIP, "Signal missing source/timestamp.")

        missing = self._missing_required_evidence(proposal.evidence)
        if missing:
            return self._blocked(
                proposal,
                DecisionAction.SKIP,
                "Missing required evidence: " + ", ".join(missing),
            )

        unsafe_claims = self._unsafe_claims(proposal)
        if unsafe_claims:
            return self._blocked(
                proposal,
                DecisionAction.SKIP,
                "Unsafe or unsupported claim language: " + ", ".join(unsafe_claims),
            )

        unsupported = self._unsupported_domain_claims(proposal)
        if unsupported:
            return self._blocked(
                proposal,
                DecisionAction.SKIP,
                "Unsupported domain claims: " + ", ".join(unsupported),
            )

        if proposal.conflict_signals:
            return VerifiedDecision(
                symbol=proposal.symbol.upper(),
                timeframe=proposal.timeframe,
                action=DecisionAction.HOLD,
                confidence=proposal.confidence,
                evidence=proposal.evidence,
                reason="Conflicting signals; holding by policy.",
                missing_data=proposal.missing_data,
                conflict_signals=proposal.conflict_signals,
                verified_decision=True,
                timestamp=proposal.timestamp,
            )

        return VerifiedDecision(
            symbol=proposal.symbol.upper(),
            timeframe=proposal.timeframe,
            action=proposal.action,
            confidence=proposal.confidence,
            evidence=proposal.evidence,
            reason=proposal.reason,
            missing_data=proposal.missing_data,
            conflict_signals=proposal.conflict_signals,
            verified_decision=True,
            timestamp=proposal.timestamp,
        )

    def _missing_required_evidence(self, evidence: list[EvidenceItem]) -> list[str]:
        available = {item.evidence_type for item in evidence}
        return sorted(item.value for item in self.required_evidence - available)

    @staticmethod
    def _unsafe_claims(proposal: DecisionProposal) -> list[str]:
        text = " ".join(
            [proposal.reason]
            + [item.summary for item in proposal.evidence]
            + [signal.name for signal in proposal.signals]
        )
        return detect_unsafe_claims(text)

    @staticmethod
    def _unsupported_domain_claims(proposal: DecisionProposal) -> list[str]:
        text = " ".join(
            [proposal.reason.lower()]
            + [item.summary.lower() for item in proposal.evidence]
            + [signal.name.lower() for signal in proposal.signals]
        )
        available = {item.evidence_type for item in proposal.evidence}
        required_by_claim = {
            "whale": EvidenceType.WHALE_SIGNAL,
            "news": EvidenceType.NEWS_SIGNAL,
            "candle": EvidenceType.CANDLE,
            "order book": EvidenceType.ORDER_BOOK,
        }
        return [
            claim
            for claim, evidence_type in required_by_claim.items()
            if claim in text and evidence_type not in available
        ]

    @staticmethod
    def _blocked(
        proposal: DecisionProposal,
        action: DecisionAction,
        rejection_reason: str,
    ) -> VerifiedDecision:
        return VerifiedDecision(
            symbol=proposal.symbol.upper(),
            timeframe=proposal.timeframe,
            action=action,
            confidence=0.0,
            evidence=proposal.evidence,
            reason=proposal.reason,
            missing_data=proposal.missing_data,
            conflict_signals=proposal.conflict_signals,
            verified_decision=False,
            rejection_reason=rejection_reason,
            timestamp=proposal.timestamp,
        )
