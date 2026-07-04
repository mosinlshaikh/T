from __future__ import annotations


def evaluate_trend(structure: dict[str, object]) -> dict[str, object]:
    trend = structure.get("structure", "unknown")
    signal = "BUY" if trend == "uptrend" else "SELL" if trend == "downtrend" else "HOLD"
    return {"strategy": "trend", "signal": signal, "evidence": [structure]}
