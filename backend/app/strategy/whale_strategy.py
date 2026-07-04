from __future__ import annotations


def evaluate_whale(signal: dict[str, object]) -> dict[str, object]:
    return {
        "strategy": "whale",
        "signal": signal.get("signal", "SKIP"),
        "evidence": signal.get("evidence", []),
    }
