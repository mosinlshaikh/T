from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from trading_os.intelligence.whale_intelligence_v1 import WhaleTrade
from trading_os.market.candle_engine import Candle
from trading_os.market.live_public_data import LiveMarketBundle
from trading_os.market.market_data_engine import RestMarketSnapshot
from trading_os.market.order_book_engine import OrderBookLevel, OrderBookSnapshot
from trading_os.market.timeframes import Timeframe
from trading_os.quality.market_data_gate import DataQualityReason, MarketDataQualityGate


def now_ms(offset_seconds: int = 0) -> int:
    return int((datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).timestamp() * 1000)


def valid_bundle() -> LiveMarketBundle:
    candles = [
        Candle(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=10.0,
            start_time_ms=now_ms(-300 - index * 300),
            end_time_ms=now_ms(-index * 300),
        )
        for index in range(25)
    ]
    trades = [
        WhaleTrade(
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.1,
            price=100.0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source="test",
        )
        for _ in range(12)
    ]
    return LiveMarketBundle(
        symbol="BTCUSDT",
        timeframe=Timeframe.FIVE_MINUTES,
        snapshot=RestMarketSnapshot(
            symbol="BTCUSDT",
            price=100.0,
            volume_24h=1000.0,
            event_time_ms=now_ms(),
            source="test",
        ),
        candles=candles,
        order_book=OrderBookSnapshot(
            symbol="BTCUSDT",
            bids=[OrderBookLevel(99.9, 1.0)],
            asks=[OrderBookLevel(100.1, 1.0)],
            event_time_ms=now_ms(),
            last_update_id=123,
            source="test",
        ),
        whale_trades=trades,
        news_items=[],
        evidence=[],
        warnings=[],
    )


def test_valid_market_bundle_passes_quality_gate() -> None:
    result = MarketDataQualityGate().validate_bundle(valid_bundle())
    assert result.valid is True
    assert result.reason_code == DataQualityReason.OK


def test_missing_bundle_returns_skip_reason() -> None:
    result = MarketDataQualityGate().validate_bundle(None)
    assert result.valid is False
    assert result.reason_code == DataQualityReason.NO_MARKET_DATA
    assert "market_bundle" in result.missing_data


def test_stale_market_data_returns_skip_reason() -> None:
    bundle = valid_bundle()
    stale = SimpleNamespace(**{**bundle.__dict__})
    stale.snapshot = RestMarketSnapshot("BTCUSDT", 100.0, 1000.0, now_ms(-9999), "test")
    result = MarketDataQualityGate().validate_bundle(stale)
    assert result.valid is False
    assert result.reason_code == DataQualityReason.STALE_MARKET_DATA


def test_invalid_best_bid_ask_returns_skip_reason() -> None:
    bundle = valid_bundle()
    invalid = SimpleNamespace(**{**bundle.__dict__})
    invalid.order_book = OrderBookSnapshot(
        symbol="BTCUSDT",
        bids=[OrderBookLevel(101.0, 1.0)],
        asks=[OrderBookLevel(100.0, 1.0)],
        last_update_id=123,
    )
    result = MarketDataQualityGate().validate_bundle(invalid)
    assert result.valid is False
    assert result.reason_code == DataQualityReason.INVALID_BEST_BID_ASK


def test_insufficient_candles_returns_skip_reason() -> None:
    bundle = valid_bundle()
    invalid = SimpleNamespace(**{**bundle.__dict__})
    invalid.candles = invalid.candles[:5]
    result = MarketDataQualityGate().validate_bundle(invalid)
    assert result.valid is False
    assert result.reason_code == DataQualityReason.INSUFFICIENT_CANDLE_WINDOW
