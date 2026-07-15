from trading_os.api.routes.monitor import (
    market_radar,
    no_trade_zone,
    paper_scan_history,
    performance_wheel,
    shadow_mode,
    strategy_blockers,
    trade_quality,
    watchlist_candidates,
)


def test_performance_wheel_is_paper_safe() -> None:
    response = performance_wheel()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["segments"]
    assert 0 <= response["data"]["overall_score"] <= 100


def test_trade_quality_blocks_when_evidence_is_missing_or_weak() -> None:
    response = trade_quality()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["recommended_action"] in {"BUY", "SELL", "HOLD", "SKIP"}
    assert isinstance(response["data"]["trade_allowed"], bool)


def test_no_trade_zone_is_safe() -> None:
    response = no_trade_zone()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["recommended_action"] in {"SKIP", "HOLD_OR_PAPER_ONLY_WATCH"}


def test_shadow_mode_never_enables_live_execution() -> None:
    response = shadow_mode()
    assert response["success"] is True
    assert response["data"]["mode"] == "PAPER_SHADOW_ONLY"
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True


def test_paper_scan_history_is_safe() -> None:
    response = paper_scan_history(limit=20)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["requested_limit"] == 20
    assert isinstance(response["data"]["rows"], list)


def test_watchlist_candidates_are_paper_safe() -> None:
    response = watchlist_candidates(limit=10)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["profit_guarantee"] is False
    assert isinstance(response["data"]["candidates"], list)


def test_strategy_blockers_are_advisory_and_paper_safe() -> None:
    response = strategy_blockers(limit=20)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["profit_guarantee"] is False
    assert "auto-changed" in response["data"]["tuning_policy"]


def test_market_radar_is_public_prefilter_only() -> None:
    response = market_radar(limit=5)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["profit_guarantee"] is False
    assert isinstance(response["data"]["deep_scan_symbols"], list)
