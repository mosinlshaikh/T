from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderBookLevel:
    price: float
    quantity: float


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: str

    def spread(self) -> float | None:
        if not self.bids or not self.asks:
            return None
        return min(ask.price for ask in self.asks) - max(bid.price for bid in self.bids)
