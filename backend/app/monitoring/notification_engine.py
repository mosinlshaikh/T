from __future__ import annotations


def notify(event_type: str, message: str) -> dict[str, object]:
    return {
        "event_type": event_type,
        "message": message,
        "dispatched": False,
        "reason": "placeholder",
    }
