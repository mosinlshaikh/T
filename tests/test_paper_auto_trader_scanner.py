from trading_os.runtime.paper_auto_trader import (
    confidence_band,
    enrich_scan_result,
    normalize_watchlist,
    trade_allowed,
    why_not_traded,
)


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
