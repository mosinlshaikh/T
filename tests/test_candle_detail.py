from trading_os.api.routes.monitor import candle_detail


def test_candle_detail_missing_data_is_safe() -> None:
    response = candle_detail(symbol="BTCUSDT", timeframe="5m", limit=40)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert "decision_rule" in response["data"]
