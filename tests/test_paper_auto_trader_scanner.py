from trading_os.runtime.paper_auto_trader import (
    PaperAutoTrader,
    confidence_band,
    enrich_scan_result,
    normalize_watchlist,
    trade_allowed,
    why_not_traded,
)
from trading_os.market.radar import rank_market_radar_rows
from trading_os.market.stream_state import MarketStreamState


class FakeAuditLogger:
    def __init__(self) -> None:
        self.events = []

    def log_skipped_trade(self, payload):
        self.events.append(("skipped_trade", payload))


class FakeBackend:
    def __init__(self) -> None:
        self.market_stream_state = MarketStreamState()
        self.audit_logger = FakeAuditLogger()


class FailingRestRadarClient:
    def fetch_all_usdt_24h_tickers(self):
        raise AssertionError("REST radar should not be called when stream cache has candidates")


class RestRadarClient:
    def fetch_all_usdt_24h_tickers(self):
        return [
            {
                "symbol": "RESTUSDT",
                "last_price": 1.0,
                "quote_volume": 5_000_000,
                "price_change_pct": 6.0,
                "volatility_pct": 8.0,
                "trade_count": 60_000,
            }
        ]


def test_normalize_watchlist_deduplicates_and_limits() -> None:
    assert normalize_watchlist(["btcusdt", "ETHUSDT", "BTCUSDT", "BAD"], 2) == [
        "BTCUSDT",
        "ETHUSDT",
    ]


def test_normalize_watchlist_supports_twenty_symbol_safe_demo_batch() -> None:
    symbols = [f"COIN{index}USDT" for index in range(25)]
    assert len(normalize_watchlist(symbols, 20)) == 20


def test_confidence_band() -> None:
    assert confidence_band(0.8) == "HIGH"
    assert confidence_band(0.5) == "MEDIUM"
    assert confidence_band(0.2) == "LOW"
    assert confidence_band(0.0) == "UNKNOWN"


def test_trade_allowed_requires_action_confidence_and_paper_open() -> None:
    assert trade_allowed("BUY", 0.75, "PAPER_OPEN") is True
    assert trade_allowed("BUY", 0.6, "PAPER_OPEN") is False
    assert trade_allowed("HOLD", 0.9, "PAPER_OPEN") is False
    assert trade_allowed("BUY", 0.9, "HOLD") is False


def test_enrich_scan_result_explains_non_trade() -> None:
    enriched = enrich_scan_result(
        {
            "symbol": "BTCUSDT",
            "action": "HOLD",
            "status": "HOLD",
            "confidence": 0.48,
            "reason": "Conflicting signals; holding by policy.",
        }
    )
    assert enriched["confidence_band"] == "MEDIUM"
    assert enriched["trade_allowed"] is False
    assert "Conflicting signals" in enriched["why_not_traded"]


def test_why_not_traded_for_low_confidence_buy() -> None:
    assert why_not_traded("BUY", 0.5, "PAPER_OPEN", "") == (
        "Confidence below paper trade threshold."
    )


def test_market_radar_ranks_public_candidates() -> None:
    rows = [
        {
            "symbol": "SLOWUSDT",
            "quote_volume": 60_000,
            "price_change_pct": 0.2,
            "volatility_pct": 0.3,
            "trade_count": 20,
        },
        {
            "symbol": "FASTUSDT",
            "quote_volume": 5_000_000,
            "price_change_pct": 8.5,
            "volatility_pct": 12.0,
            "trade_count": 80_000,
        },
    ]

    ranked = rank_market_radar_rows(rows, limit=2)

    assert ranked[0]["symbol"] == "FASTUSDT"
    assert ranked[0]["deep_scan_recommended"] is True


def test_paper_scanner_prefers_fast_market_stream_cache() -> None:
    backend = FakeBackend()
    backend.market_stream_state.update_many(
        [
            {
                "symbol": "CACHEUSDT",
                "last_price": 2.0,
                "quote_volume": 10_000_000,
                "price_change_pct": 7.0,
                "high_price": 2.2,
                "low_price": 1.8,
                "source": "binance_public_miniticker_stream",
            }
        ]
    )
    trader = PaperAutoTrader(backend)

    symbols, source = trader._radar_shortlist(5, FailingRestRadarClient())

    assert symbols == ["CACHEUSDT"]
    assert source == "FAST_MARKET_STREAM_CACHE"


def test_paper_scanner_falls_back_to_rest_radar_when_cache_empty() -> None:
    trader = PaperAutoTrader(FakeBackend())

    symbols, source = trader._radar_shortlist(5, RestRadarClient())

    assert symbols == ["RESTUSDT"]
    assert source == "PUBLIC_24HR_REST_RADAR"
