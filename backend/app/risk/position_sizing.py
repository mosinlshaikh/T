from __future__ import annotations


def size_position(balance: float, risk_pct: float = 5.0) -> float:
    return round(balance * min(risk_pct, 5.0) / 100, 8)
