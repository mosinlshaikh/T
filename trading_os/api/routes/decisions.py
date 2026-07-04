from __future__ import annotations

from trading_os.api.dependencies import latest_audit_events
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok

router = APIRouter(prefix="/decisions", tags=["decisions"])


def _decision_payload(event: dict[str, object]) -> dict[str, object]:
    payload = event.get("payload", event)
    if not isinstance(payload, dict):
        payload = {}
    return {
        "decision_id": event.get("event_id", event.get("record_id", "")),
        "timestamp": event.get("created_at", payload.get("timestamp", "")),
        "action": payload.get("action", "SKIP"),
        "confidence": payload.get("confidence", 0.0),
        "evidence": payload.get("evidence", []),
        "reason": payload.get("reason", ""),
        "missing_data": payload.get("missing_data", []),
        "conflicts": payload.get("conflict_signals", []),
        "zero_hallucination_verified": payload.get("verified", False),
        "risk_status": payload.get("risk_status", "unknown"),
        "rejection_reason": payload.get("rejection_reason", ""),
    }


def _decisions(limit: int = 50) -> list[dict[str, object]]:
    return [_decision_payload(event) for event in latest_audit_events(limit, "ai_decision")]


@router.get("/latest")
def latest_decision() -> dict[str, object]:
    decisions = _decisions(limit=1)
    return ok(decisions[0] if decisions else None, "Latest decision loaded.")


@router.get("/history")
def decision_history() -> dict[str, object]:
    return ok(_decisions(limit=100), "Decision history loaded.")


@router.get("/skipped")
def skipped_decisions() -> dict[str, object]:
    return ok(
        [item for item in _decisions(100) if item["action"] == "SKIP"], "Skipped decisions loaded."
    )


@router.get("/blocked")
def blocked_decisions() -> dict[str, object]:
    blocked = [
        item
        for item in _decisions(100)
        if not item["zero_hallucination_verified"] or item["rejection_reason"]
    ]
    return ok(blocked, "Blocked decisions loaded.")


@router.get("/{decision_id}")
def decision_by_id(decision_id: str) -> dict[str, object]:
    for item in _decisions(200):
        if item["decision_id"] == decision_id:
            return ok(item, "Decision loaded.")
    return ok(None, "Decision not found.", warnings=["Unknown decision_id."])
