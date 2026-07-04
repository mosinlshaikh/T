from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.binance.rest_client import BinanceRestClient
from backend.app.binance.websocket_client import BinanceWebSocketClient


@dataclass
class BinanceSpotClient:
    rest: BinanceRestClient = field(default_factory=BinanceRestClient)
    websocket: BinanceWebSocketClient = field(default_factory=BinanceWebSocketClient)
    live_trading_enabled: bool = False

    def execute_order(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Real Binance order execution is disabled.")
