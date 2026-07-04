from __future__ import annotations


def evaluate_news(signal: dict[str, object]) -> dict[str, object]:
    return {
        "strategy": "news",
        "signal": signal.get("signal", "SKIP"),
        "evidence": signal.get("evidence", []),
    }
