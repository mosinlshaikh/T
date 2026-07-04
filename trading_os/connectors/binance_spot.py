from __future__ import annotations

from dataclasses import dataclass

from trading_os.connectors.rest_api import RestApiConnector, RestApiRequest
from trading_os.connectors.websocket_market_data import (
    WebSocketMarketDataConnector,
    WebSocketSubscription,
)


@dataclass
class BinanceSpotConnector:
    """Binance Spot connector skeleton.

    Live order execution is intentionally unavailable. This connector only
    prepares public market-data requests and rejects live orders.
    """

    rest_api: RestApiConnector
    websocket_market_data: WebSocketMarketDataConnector
    live_trading_enabled: bool = False

    def latest_price_request(self, symbol: str) -> RestApiRequest:
        return self.rest_api.build_public_request(
            "/api/v3/ticker/price", {"symbol": symbol.upper()}
        )

    def order_book_request(self, symbol: str, limit: int = 100) -> RestApiRequest:
        return self.rest_api.build_public_request(
            "/api/v3/depth", {"symbol": symbol.upper(), "limit": limit}
        )

    def trades_subscription(self, symbol: str) -> WebSocketSubscription:
        return self.websocket_market_data.build_subscription(symbol, "aggTrade")

    def execute_order(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Live trading execution is disabled by default and not implemented.")
