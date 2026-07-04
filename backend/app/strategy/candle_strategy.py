from __future__ import annotations


def evaluate_candle(signal: dict[str, object]) -> dict[str, object]:
    return {
        "strategy": "candle",
        "signal": signal.get("signal", "SKIP"),
        "evidence": signal.get("evidence", []),
    }
