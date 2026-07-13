from trading_os.api.routes.monitor import market_evidence_feed


def test_market_evidence_feed_is_safe() -> None:
    response = market_evidence_feed()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["rule"] == "No Data = No Trade; No Proof = No Decision"
    assert "items" in response["data"]
