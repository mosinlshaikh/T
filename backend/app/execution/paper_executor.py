from __future__ import annotations


def execute_paper_order(intent: dict[str, object]) -> dict[str, object]:
    return {"mode": "paper", "executed": True, "intent": intent}
