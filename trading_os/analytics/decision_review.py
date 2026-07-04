from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from trading_os.db.repository import TradingOSRepository


class DecisionReviewResult(str, Enum):
    GOOD_DECISION = "GOOD_DECISION"
    BAD_DECISION = "BAD_DECISION"
    INCOMPLETE_DATA = "INCOMPLETE_DATA"
    RISK_BLOCKED = "RISK_BLOCKED"
    HALLUCINATION_BLOCKED = "HALLUCINATION_BLOCKED"
    NOT_ENOUGH_HISTORY = "NOT_ENOUGH_HISTORY"


@dataclass(frozen=True)
class DecisionReview:
    decision_id: str
    result: DecisionReviewResult
    reason: str
    evidence_references: list[str] = field(default_factory=list)
    decision_type: str = "SKIP"
    confidence: float = 0.0
    evidence_quality: str = "unknown"
    missing_data: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    zero_hallucination_verified: bool = False
    risk_result: str = "unknown"
    execution_intent_result: str = "unknown"
    final_paper_outcome: str = "unknown"


@dataclass
class DecisionReviewEngine:
    repository: TradingOSRepository

    def review_latest(self, limit: int = 20) -> list[DecisionReview]:
        decisions = self.repository.list_ai_decisions(limit)
        if not decisions:
            return [
                DecisionReview(
                    decision_id="",
                    result=DecisionReviewResult.NOT_ENOUGH_HISTORY,
                    reason="No persisted decisions available.",
                )
            ]
        return [self.review(decision, index) for index, decision in enumerate(decisions)]

    def review(self, decision: dict[str, Any], index: int = 0) -> DecisionReview:
        decision_id = str(decision.get("decision_id") or decision.get("event_id") or index)
        missing = list(decision.get("missing_data", []) or [])
        conflicts = list(decision.get("conflict_signals", decision.get("conflicts", [])) or [])
        evidence = list(decision.get("evidence", []) or [])
        verified = bool(decision.get("verified", decision.get("verified_decision", False)))
        action = str(decision.get("action", "SKIP"))
        risk_status = str(decision.get("risk_status", "unknown"))
        evidence_refs = [
            str(item.get("source") or item.get("type") or item.get("summary"))
            for item in evidence
            if isinstance(item, dict)
        ]

        if not verified:
            result = DecisionReviewResult.HALLUCINATION_BLOCKED
            reason = "Decision was not zero-hallucination verified."
        elif risk_status == "rejected":
            result = DecisionReviewResult.RISK_BLOCKED
            reason = "Risk engine rejected the decision."
        elif missing or conflicts:
            result = DecisionReviewResult.INCOMPLETE_DATA
            reason = "Decision contains missing data or conflicting signals."
        elif action in {"HOLD", "SKIP"}:
            result = DecisionReviewResult.NOT_ENOUGH_HISTORY
            reason = "No final paper trade outcome is expected for HOLD/SKIP."
        else:
            outcome = self._outcome_for_decision(decision)
            if outcome == "unknown":
                result = DecisionReviewResult.NOT_ENOUGH_HISTORY
                reason = "Final paper outcome is not available."
            elif outcome == "win":
                result = DecisionReviewResult.GOOD_DECISION
                reason = "Persisted paper outcome was positive."
            else:
                result = DecisionReviewResult.BAD_DECISION
                reason = "Persisted paper outcome was negative."

        return DecisionReview(
            decision_id=decision_id,
            result=result,
            reason=reason,
            evidence_references=evidence_refs,
            decision_type=action,
            confidence=float(decision.get("confidence", 0.0) or 0.0),
            evidence_quality=self._evidence_quality(evidence),
            missing_data=missing,
            conflicts=conflicts,
            zero_hallucination_verified=verified,
            risk_result=risk_status,
            execution_intent_result=self._execution_result(),
            final_paper_outcome=self._outcome_for_decision(decision),
        )

    def _execution_result(self) -> str:
        intents = self.repository.list_execution_intents(1)
        return "available" if intents else "unknown"

    def _outcome_for_decision(self, _decision: dict[str, Any]) -> str:
        journal = self.repository.list_trade_journal(100)
        pnl_values = [float(item.get("realized_pnl", 0.0) or 0.0) for item in journal]
        if not pnl_values:
            return "unknown"
        latest = pnl_values[-1]
        if latest > 0:
            return "win"
        if latest < 0:
            return "loss"
        return "flat"

    @staticmethod
    def _evidence_quality(evidence: list[Any]) -> str:
        if not evidence:
            return "missing"
        valid = [
            item
            for item in evidence
            if isinstance(item, dict) and item.get("source") and item.get("timestamp")
        ]
        if len(valid) == len(evidence):
            return "complete"
        return "partial"
