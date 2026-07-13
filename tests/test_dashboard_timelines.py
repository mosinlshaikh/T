from trading_os.api.routes.reports import dashboard_timelines


def test_dashboard_timelines_are_safe() -> None:
    response = dashboard_timelines()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert "decision_timeline" in response["data"]
    assert "trade_timeline" in response["data"]
    assert "audit_timeline" in response["data"]
