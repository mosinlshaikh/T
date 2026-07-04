from __future__ import annotations


def audit_record(event_type: str, payload: dict[str, object]) -> dict[str, object]:
    return {"event_type": event_type, "payload": payload}
