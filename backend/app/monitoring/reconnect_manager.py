from __future__ import annotations


def reconnect_state(attempts: int) -> dict[str, object]:
    return {"attempts": attempts, "next_action": "backoff" if attempts else "connected"}
