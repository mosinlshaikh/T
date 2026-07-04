from __future__ import annotations

from dataclasses import dataclass

from backend.app.decision import decision_reasons


@dataclass(frozen=True)
class VerificationResult:
    allowed: bool
    reason: str


def verify_decision(decision: dict[str, object]) -> VerificationResult:
    evidence = decision.get("evidence_snapshot") or []
    if not evidence:
        return VerificationResult(False, decision_reasons.NO_PROOF)
    if decision.get("binance_connection_unstable"):
        return VerificationResult(False, "Binance connection unstable.")
    if decision.get("candle_missing"):
        return VerificationResult(False, "Candle data missing.")
    return VerificationResult(True, "Verified evidence present.")
