from trading_os.api.routes.reports import dashboard_charts


def test_dashboard_charts_are_safe() -> None:
    response = dashboard_charts()

    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert set(response["data"]["action_counts"]) == {"BUY", "SELL", "HOLD", "SKIP"}
