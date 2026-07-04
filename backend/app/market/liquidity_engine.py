from __future__ import annotations

from backend.app.market.order_book_engine import OrderBookSnapshot


def liquidity_gap(snapshot: OrderBookSnapshot) -> dict[str, object]:
    spread = snapshot.spread()
    if spread is None:
        return {"risk": "unknown", "missing_data": ["order_book"]}
    return {"risk": "high" if spread > 0 else "normal", "spread": spread}
