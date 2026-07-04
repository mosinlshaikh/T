from __future__ import annotations


def combine_strategies(strategies: list[dict[str, object]]) -> dict[str, object]:
    if not strategies:
        return {"signal": "SKIP", "confidence": 0.0, "reason": "No strategies."}
    signals = {item.get("signal", "SKIP") for item in strategies}
    if "SKIP" in signals:
        return {"signal": "SKIP", "confidence": 0.0, "reason": "Required strategy data missing."}
    if "BUY" in signals and "SELL" in signals:
        return {"signal": "SKIP", "confidence": 0.0, "reason": "Signals conflict."}
    confirmations = len([item for item in strategies if item.get("signal") in {"BUY", "SELL"}])
    if confirmations < 2:
        return {"signal": "SKIP", "confidence": 0.0, "reason": "Multi-confirmation required."}
    signal = "BUY" if "BUY" in signals else "SELL" if "SELL" in signals else "HOLD"
    return {
        "signal": signal,
        "confidence": min(confirmations / len(strategies), 1.0),
        "reason": "Multi-confirmation evidence.",
    }
