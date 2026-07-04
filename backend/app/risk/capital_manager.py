from __future__ import annotations


def capital_buckets(balance: float) -> dict[str, float]:
    return {
        "reserve_capital": round(balance * 0.10, 8),
        "max_active_risk": round(balance * 0.05, 8),
        "growth_capital": round(balance * 0.85, 8),
    }
