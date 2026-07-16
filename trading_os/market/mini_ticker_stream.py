from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import websockets

from trading_os.market.stream_state import MarketStreamState

BINANCE_MINI_TICKER_STREAM_URL = "wss://stream.binance.com:9443/ws/!miniTicker@arr"


@dataclass
class MiniTickerStreamStatus:
    running: bool
    connected: bool
    reconnect_attempts: int
    last_error: str
    public_data_only: bool = True
    live_trading_enabled: bool = False


class BinanceMiniTickerStream:
    """Public Binance miniTicker stream adapter.

    This class is intentionally market-data only. It never signs requests,
    reads credentials, places orders, or changes live-trading state.
    """

    def __init__(
        self,
        state: MarketStreamState,
        url: str = BINANCE_MINI_TICKER_STREAM_URL,
        reconnect_delay_seconds: float = 3.0,
    ) -> None:
        self.state = state
        self.url = url
        self.reconnect_delay_seconds = reconnect_delay_seconds
        self._running = False
        self._connected = False
        self._reconnect_attempts = 0
        self._last_error = ""

    async def run_forever(self) -> None:
        self._running = True
        while self._running:
            try:
                async with websockets.connect(self.url, ping_interval=20) as websocket:
                    self._connected = True
                    self._last_error = ""
                    async for message in websocket:
                        if not self._running:
                            break
                        self.handle_message(message)
            except Exception as exc:
                self._connected = False
                self._reconnect_attempts += 1
                self._last_error = f"{exc.__class__.__name__}: stream reconnect scheduled"
                await asyncio.sleep(self.reconnect_delay_seconds)
            finally:
                self._connected = False

    def stop(self) -> None:
        self._running = False

    def handle_message(self, message: str | bytes) -> dict[str, int]:
        payload = json.loads(message.decode("utf-8") if isinstance(message, bytes) else message)
        rows: list[dict[str, Any]] = payload if isinstance(payload, list) else [payload]
        normalized = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("s", "")).upper()
            if not symbol.endswith("USDT"):
                continue
            normalized.append(
                {
                    "symbol": symbol,
                    "last_price": item.get("c", 0.0),
                    "quote_volume": item.get("q", 0.0),
                    "volume": item.get("v", 0.0),
                    "high_price": item.get("h", 0.0),
                    "low_price": item.get("l", 0.0),
                    "event_time_ms": item.get("E", 0),
                    "source": "binance_public_miniticker_stream",
                }
            )
        return self.state.update_many(normalized, source="binance_public_miniticker_stream")

    def status(self) -> dict[str, object]:
        return MiniTickerStreamStatus(
            running=self._running,
            connected=self._connected,
            reconnect_attempts=self._reconnect_attempts,
            last_error=self._last_error,
        ).__dict__
