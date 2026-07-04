from __future__ import annotations


def check_permissions(metadata: dict[str, bool]) -> dict[str, object]:
    if metadata.get("withdrawals"):
        return {"status": "BLOCKED", "reason": "Withdraw permission must be off."}
    if not metadata.get("read", False):
        return {"status": "MISCONFIGURED", "reason": "Read permission expected."}
    return {"status": "READY_FOR_PAPER", "reason": "Safe paper readiness."}
