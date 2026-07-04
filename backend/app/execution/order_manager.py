from __future__ import annotations


def create_order_intent(symbol: str, side: str, quantity: float, reason: str) -> dict[str, object]:
    return {
        "symbol": symbol.upper(),
        "side": side,
        "quantity": quantity,
        "reason": reason,
        "live_enabled": False,
    }
