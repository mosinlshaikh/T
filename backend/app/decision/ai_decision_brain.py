from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from backend.app.decision import decision_reasons
from backend.app.decision.zero_hallucination_engine import verify_decision

ALLOWED_DECISIONS = {"BUY", "SELL", "HOLD", "SKIP"}


@dataclass(frozen=True)
class AIDecision:
    timestamp: str
    symbol: str
    price: float
    evidence_snapshot: list[dict[str, object]]
    confidence_score: float
    final_decision: str
    reason: str


@dataclass
class AIDecisionBrain:
    minimum_confidence: float = 0.65
    required_inputs: set[str] = field(default_factory=lambda: {"candle", "risk", "strategy"})

    def decide(
        self,
        symbol: str,
        price: float,
        inputs: dict[str, dict[str, object]],
    ) -> AIDecision:
        missing = sorted(self.required_inputs - set(inputs))
        evidence = [value for value in inputs.values() if value.get("evidence")]
        if missing:
            return self._decision(symbol, price, evidence, 0.0, "SKIP", f"Missing data: {missing}")
        strategy = inputs["strategy"]
        risk = inputs["risk"]
        confidence = float(strategy.get("confidence", 0.0))
        final = str(strategy.get("signal", "SKIP"))
        if risk.get("status") != "SAFE":
            final, reason = "SKIP", decision_reasons.RISK_UNSAFE
        elif final not in ALLOWED_DECISIONS:
            final, reason = "SKIP", "Invalid decision output."
        elif confidence < self.minimum_confidence:
            final, reason = "SKIP", decision_reasons.LOW_CONFIDENCE
        else:
            reason = str(strategy.get("reason", "Evidence-based decision."))
        candidate = self._decision(symbol, price, evidence, confidence, final, reason)
        verification = verify_decision(candidate.__dict__)
        if not verification.allowed:
            return self._decision(symbol, price, evidence, confidence, "SKIP", verification.reason)
        return candidate

    @staticmethod
    def _decision(
        symbol: str,
        price: float,
        evidence: list[dict[str, object]],
        confidence: float,
        final: str,
        reason: str,
    ) -> AIDecision:
        return AIDecision(
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=symbol.upper(),
            price=price,
            evidence_snapshot=evidence,
            confidence_score=round(confidence, 4),
            final_decision=final,
            reason=reason,
        )
