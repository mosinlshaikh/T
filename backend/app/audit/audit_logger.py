from __future__ import annotations

from backend.app.security.secret_policy import redact


def log_event(event_type: str, payload: dict[str, object]) -> dict[str, object]:
    return {"event_type": event_type, "payload": redact(payload)}
