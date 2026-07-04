from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WebSocketSubscription:
    symbol: str
    stream: str


@dataclass(frozen=True)
class LiveTickerMessage:
    symbol: str
    price: float
    volume: float
    event_time_ms: int
    source: str = "binance_ws_ticker"


@dataclass
class WebSocketMarketDataConnector:
    """WebSocket market-data connector skeleton.

    Public market-data streams only. No account/order streams are enabled here.
    """

    base_url: str = "wss://stream.binance.com:9443/ws"

    def build_subscription(self, symbol: str, stream: str = "trade") -> WebSocketSubscription:
        return WebSocketSubscription(symbol=symbol.lower(), stream=stream)

    def live_ticker_subscription(self, symbol: str) -> WebSocketSubscription:
        return self.build_subscription(symbol, "ticker")

    def stream_url(self, subscription: WebSocketSubscription) -> str:
        return f"{self.base_url}/{subscription.symbol}@{subscription.stream}"
