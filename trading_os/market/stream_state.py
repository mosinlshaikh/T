from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Lock
from time import time
from typing import Any

from trading_os.market.radar import rank_market_radar_rows


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class StreamingTicker:
    symbol: str
    last_price: float
    price_change_pct: float = 0.0
    quote_volume: float = 0.0
    volume: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    trade_count: int = 0
    event_time_ms: int = 0
    updated_at: str = ""
    source: str = "market_stream_state"

    def to_radar_row(self) -> dict[str, Any]:
        volatility_pct = (
            ((self.high_price - self.low_price) / self.last_price * 100)
            if self.last_price and self.high_price and self.low_price
            else 0.0
        )
        return {
            "symbol": self.symbol,
            "last_price": self.last_price,
            "quote_volume": self.quote_volume,
            "price_change_pct": self.price_change_pct,
            "volatility_pct": round(volatility_pct, 4),
            "trade_count": self.trade_count,
            "event_time_ms": self.event_time_ms,
            "updated_at": self.updated_at,
            "source": self.source,
        }


class MarketStreamState:
    """Thread-safe public market cache for low-latency paper scan prefilters.

    The state stores public ticker data only. It does not store secrets, cannot
    place orders, and does not enable live trading.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._tickers: dict[str, StreamingTicker] = {}
        self._last_update_at: str = ""
        self._last_update_epoch: float = 0.0
        self._update_count = 0

    def update_ticker(self, row: dict[str, Any], source: str | None = None) -> StreamingTicker:
        symbol = str(row.get("symbol", "")).upper().strip()
        if not symbol:
            raise ValueError("ticker symbol is required")
        last_price = self._float(row, "last_price", "lastPrice", "c")
        if last_price <= 0:
            raise ValueError(f"{symbol} last price must be positive")
        ticker = StreamingTicker(
            symbol=symbol,
            last_price=last_price,
            price_change_pct=self._float(row, "price_change_pct", "priceChangePercent", "P"),
            quote_volume=self._float(row, "quote_volume", "quoteVolume", "q"),
            volume=self._float(row, "volume", "volume_24h", "v"),
            high_price=self._float(row, "high_price", "highPrice", "h"),
            low_price=self._float(row, "low_price", "lowPrice", "l"),
            trade_count=int(self._float(row, "trade_count", "count", default=0.0)),
            event_time_ms=int(self._float(row, "event_time_ms", "closeTime", "E", default=0.0)),
            updated_at=utc_now(),
            source=source or str(row.get("source") or "market_stream_state"),
        )
        with self._lock:
            self._tickers[symbol] = ticker
            self._last_update_at = ticker.updated_at
            self._last_update_epoch = time()
            self._update_count += 1
        return ticker

    def update_many(self, rows: list[dict[str, Any]], source: str | None = None) -> dict[str, int]:
        accepted = 0
        rejected = 0
        for row in rows:
            try:
                self.update_ticker(row, source=source)
                accepted += 1
            except (TypeError, ValueError):
                rejected += 1
        return {"accepted": accepted, "rejected": rejected}

    def snapshot(self, limit: int | None = None) -> list[dict[str, Any]]:
        with self._lock:
            rows = [ticker.to_radar_row() for ticker in self._tickers.values()]
        rows = sorted(rows, key=lambda item: str(item["symbol"]))
        if limit is None:
            return rows
        safe_limit = min(max(int(limit), 1), 500)
        return rows[:safe_limit]

    def ranked_radar(self, limit: int = 30) -> list[dict[str, object]]:
        return rank_market_radar_rows(self.snapshot(), limit=limit)

    def health(self) -> dict[str, object]:
        now = time()
        age_seconds = round(now - self._last_update_epoch, 3) if self._last_update_epoch else None
        return {
            "ticker_count": len(self._tickers),
            "last_update_at": self._last_update_at or "UNKNOWN",
            "last_update_age_seconds": age_seconds,
            "update_count": self._update_count,
            "stream_cache_ready": bool(self._tickers),
            "live_trading_enabled": False,
            "public_data_only": True,
        }

    def as_dict(self) -> dict[str, object]:
        return {"health": self.health(), "tickers": [asdict(t) for t in self._tickers.values()]}

    @staticmethod
    def _float(row: dict[str, Any], *keys: str, default: float = 0.0) -> float:
        for key in keys:
            if key not in row:
                continue
            try:
                return float(row.get(key, default) or default)
            except (TypeError, ValueError):
                return default
        return default
