from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OrderBookLevel:
    price: float
    quantity: float


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    event_time_ms: int = 0
    last_update_id: int | None = None
    source: str = "binance_public"


@dataclass
class OrderBookEngine:
    snapshots: dict[str, OrderBookSnapshot] = field(default_factory=dict)

    def update_snapshot(self, snapshot: OrderBookSnapshot) -> None:
        if not snapshot.bids or not snapshot.asks:
            raise ValueError("Order book snapshot requires at least one bid and one ask.")
        self.snapshots[snapshot.symbol.upper()] = snapshot

    def spread(self, symbol: str) -> float | None:
        snapshot = self.snapshots.get(symbol.upper())
        if snapshot is None:
            return None
        best_bid = max(level.price for level in snapshot.bids)
        best_ask = min(level.price for level in snapshot.asks)
        return round(best_ask - best_bid, 8)
