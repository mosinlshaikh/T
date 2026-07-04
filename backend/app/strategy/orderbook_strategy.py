from __future__ import annotations


def evaluate_order_book(signal: dict[str, object]) -> dict[str, object]:
    return {
        "strategy": "order_book",
        "signal": signal.get("signal", "SKIP"),
        "evidence": signal.get("evidence", []),
    }
