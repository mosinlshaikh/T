from trading_os.api.routes.monitor import paper_demo_readiness, paper_scan_summary


def test_paper_scan_summary_is_safe() -> None:
    response = paper_scan_summary()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert "latest_action" in response["data"]
    assert "why_not_traded" in response["data"]


def test_paper_demo_readiness_is_safe() -> None:
    response = paper_demo_readiness()
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert response["data"]["real_money_ready"] is False
    assert "paper_backend_apk_monitoring_percent" in response["data"]
    assert "paper_demo_readiness_percent" in response["data"]
