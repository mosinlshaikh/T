from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any


class DataQualityReason(str, Enum):
    OK = "OK"
    NO_MARKET_DATA = "NO_MARKET_DATA"
    STALE_MARKET_DATA = "STALE_MARKET_DATA"
    ORDER_BOOK_NOT_SYNCHRONIZED = "ORDER_BOOK_NOT_SYNCHRONIZED"
    ORDER_BOOK_SEQUENCE_GAP = "ORDER_BOOK_SEQUENCE_GAP"
    INVALID_BEST_BID_ASK = "INVALID_BEST_BID_ASK"
    INSUFFICIENT_TRADE_WINDOW = "INSUFFICIENT_TRADE_WINDOW"
    INSUFFICIENT_CANDLE_WINDOW = "INSUFFICIENT_CANDLE_WINDOW"
    CLOCK_SKEW_EXCEEDED = "CLOCK_SKEW_EXCEEDED"
    UNKNOWN_INSTRUMENT = "UNKNOWN_INSTRUMENT"
    FEATURE_WINDOW_INCOMPLETE = "FEATURE_WINDOW_INCOMPLETE"


@dataclass(frozen=True)
class DataQualityResult:
    valid: bool
    reason_code: DataQualityReason
    missing_data: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, evidence: dict[str, Any]) -> "DataQualityResult":
        return cls(valid=True, reason_code=DataQualityReason.OK, evidence=evidence)

    @classmethod
    def skip(
        cls,
        reason_code: DataQualityReason,
        missing_data: list[str] | None = None,
        conflicts: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> "DataQualityResult":
        return cls(
            valid=False,
            reason_code=reason_code,
            missing_data=missing_data or [],
            conflicts=conflicts or [],
            evidence=evidence or {},
        )


@dataclass(frozen=True)
class MarketDataQualityGate:
    max_market_age_seconds: int = 300
    clock_tolerance_seconds: int = 30
    min_candles: int = 20
    min_trades: int = 10

    def validate_bundle(self, bundle: Any) -> DataQualityResult:
        if bundle is None:
            return DataQualityResult.skip(
                DataQualityReason.NO_MARKET_DATA, missing_data=["market_bundle"]
            )
        symbol = str(getattr(bundle, "symbol", "") or "").upper()
        if not symbol or not symbol.endswith("USDT"):
            return DataQualityResult.skip(
                DataQualityReason.UNKNOWN_INSTRUMENT,
                missing_data=["instrument"],
                evidence={"symbol": symbol},
            )

        snapshot = getattr(bundle, "snapshot", None)
        if snapshot is None:
            return DataQualityResult.skip(
                DataQualityReason.NO_MARKET_DATA,
                missing_data=["snapshot"],
                evidence={"symbol": symbol},
            )
        price = float(getattr(snapshot, "price", 0.0) or 0.0)
        if not isfinite(price) or price <= 0:
            return DataQualityResult.skip(
                DataQualityReason.NO_MARKET_DATA,
                missing_data=["valid_price"],
                evidence={"symbol": symbol, "price": price},
            )

        time_result = self._validate_event_time(getattr(snapshot, "event_time_ms", 0), symbol)
        if not time_result.valid:
            return time_result

        candles = list(getattr(bundle, "candles", []) or [])
        if len(candles) < self.min_candles:
            return DataQualityResult.skip(
                DataQualityReason.INSUFFICIENT_CANDLE_WINDOW,
                missing_data=["candles"],
                evidence={"symbol": symbol, "candles": len(candles), "required": self.min_candles},
            )

        order_book = getattr(bundle, "order_book", None)
        book_result = self._validate_order_book(order_book, symbol)
        if not book_result.valid:
            return book_result

        trades = list(getattr(bundle, "whale_trades", []) or [])
        if len(trades) < self.min_trades:
            return DataQualityResult.skip(
                DataQualityReason.INSUFFICIENT_TRADE_WINDOW,
                missing_data=["trades"],
                evidence={"symbol": symbol, "trades": len(trades), "required": self.min_trades},
            )

        return DataQualityResult.ok(
            {
                "symbol": symbol,
                "price": price,
                "candles": len(candles),
                "trades": len(trades),
                "order_book_bids": len(getattr(order_book, "bids", []) or []),
                "order_book_asks": len(getattr(order_book, "asks", []) or []),
                "last_update_id": int(getattr(order_book, "last_update_id", 0) or 0),
            }
        )

    def _validate_event_time(self, event_time_ms: int, symbol: str) -> DataQualityResult:
        if not event_time_ms:
            return DataQualityResult.skip(
                DataQualityReason.STALE_MARKET_DATA,
                missing_data=["event_time_ms"],
                evidence={"symbol": symbol},
            )
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        age_seconds = (now_ms - int(event_time_ms)) / 1000
        if age_seconds < -self.clock_tolerance_seconds:
            return DataQualityResult.skip(
                DataQualityReason.CLOCK_SKEW_EXCEEDED,
                conflicts=["market_timestamp_in_future"],
                evidence={"symbol": symbol, "age_seconds": round(age_seconds, 3)},
            )
        if age_seconds > self.max_market_age_seconds:
            return DataQualityResult.skip(
                DataQualityReason.STALE_MARKET_DATA,
                conflicts=["market_timestamp_stale"],
                evidence={"symbol": symbol, "age_seconds": round(age_seconds, 3)},
            )
        return DataQualityResult.ok({"symbol": symbol, "age_seconds": round(age_seconds, 3)})

    def _validate_order_book(self, order_book: Any, symbol: str) -> DataQualityResult:
        if order_book is None:
            return DataQualityResult.skip(
                DataQualityReason.ORDER_BOOK_NOT_SYNCHRONIZED,
                missing_data=["order_book"],
                evidence={"symbol": symbol},
            )
        bids = list(getattr(order_book, "bids", []) or [])
        asks = list(getattr(order_book, "asks", []) or [])
        last_update_id = int(getattr(order_book, "last_update_id", 0) or 0)
        if last_update_id <= 0:
            return DataQualityResult.skip(
                DataQualityReason.ORDER_BOOK_NOT_SYNCHRONIZED,
                missing_data=["last_update_id"],
                evidence={"symbol": symbol, "last_update_id": last_update_id},
            )
        if not bids or not asks:
            return DataQualityResult.skip(
                DataQualityReason.ORDER_BOOK_NOT_SYNCHRONIZED,
                missing_data=["bids" if not bids else "asks"],
                evidence={"symbol": symbol, "bids": len(bids), "asks": len(asks)},
            )
        best_bid = float(getattr(bids[0], "price", 0.0) or 0.0)
        best_ask = float(getattr(asks[0], "price", 0.0) or 0.0)
        quantities = [
            float(getattr(level, "quantity", 0.0) or 0.0) for level in [*bids[:20], *asks[:20]]
        ]
        if any((not isfinite(value) or value < 0) for value in [best_bid, best_ask, *quantities]):
            return DataQualityResult.skip(
                DataQualityReason.INVALID_BEST_BID_ASK,
                conflicts=["non_finite_or_negative_book_value"],
                evidence={"symbol": symbol},
            )
        if best_bid <= 0 or best_ask <= 0 or best_bid >= best_ask:
            return DataQualityResult.skip(
                DataQualityReason.INVALID_BEST_BID_ASK,
                conflicts=["best_bid_must_be_below_best_ask"],
                evidence={"symbol": symbol, "best_bid": best_bid, "best_ask": best_ask},
            )
        return DataQualityResult.ok(
            {
                "symbol": symbol,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "last_update_id": last_update_id,
            }
        )
