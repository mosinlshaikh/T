from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BinanceWebSocketClient:
    stream_base_url: str = "wss://stream.binance.com:9443/ws"
    connected: bool = False

    def ticker_stream_url(self, symbol: str) -> str:
        return f"{self.stream_base_url}/{symbol.lower()}@ticker"

    def mark_unstable(self) -> None:
        self.connected = False
