from __future__ import annotations


def decision_audit_payload(decision: dict[str, object], executed: bool) -> dict[str, object]:
    payload = dict(decision)
    payload["executed"] = executed
    return payload
