from __future__ import annotations


def journal_entry(symbol: str, action: str, reason: str) -> dict[str, object]:
    return {"symbol": symbol.upper(), "action": action, "reason": reason, "mode": "paper"}
