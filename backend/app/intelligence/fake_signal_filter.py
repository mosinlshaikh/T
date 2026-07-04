from __future__ import annotations


def reject_unsupported_claim(signal: dict[str, object]) -> dict[str, object]:
    if not signal.get("evidence") and signal.get("signal") in {"BUY", "SELL"}:
        return {"signal": "SKIP", "reason": "Unsupported claim rejected."}
    return signal
