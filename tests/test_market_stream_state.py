from trading_os.market.mini_ticker_stream import BinanceMiniTickerStream
from trading_os.market.stream_state import MarketStreamState


def test_market_stream_state_updates_and_ranks_public_tickers() -> None:
    state = MarketStreamState()
    result = state.update_many(
        [
            {
                "symbol": "BTCUSDT",
                "last_price": 100000,
                "quote_volume": 500000000,
                "price_change_pct": 2.5,
                "high_price": 103000,
                "low_price": 98000,
                "trade_count": 150000,
            },
            {
                "symbol": "LOWUSDT",
                "last_price": 1,
                "quote_volume": 100,
                "trade_count": 1,
            },
        ],
        source="test_public_ticker",
    )

    assert result == {"accepted": 2, "rejected": 0}
    health = state.health()
    assert health["stream_cache_ready"] is True
    assert health["ticker_count"] == 2
    assert health["live_trading_enabled"] is False
    ranked = state.ranked_radar(limit=5)
    assert ranked[0]["symbol"] == "BTCUSDT"
    assert ranked[0]["deep_scan_recommended"] is True


def test_mini_ticker_stream_message_updates_public_cache_only() -> None:
    state = MarketStreamState()
    stream = BinanceMiniTickerStream(state)

    result = stream.handle_message(
        '[{"e":"24hrMiniTicker","E":123,"s":"ETHUSDT","c":"2500",'
        '"o":"2400","h":"2600","l":"2300","v":"1000","q":"2500000"}]'
    )

    assert result["accepted"] == 1
    health = state.health()
    assert health["ticker_count"] == 1
    assert health["public_data_only"] is True
    status = stream.status()
    assert status["live_trading_enabled"] is False
    assert status["public_data_only"] is True
