from trading_os.derivatives.risk import DerivativesRiskGuard


def test_derivatives_readiness_blocks_live_execution() -> None:
    report = DerivativesRiskGuard().readiness(live_trading_enabled=True)
    assert report["futures_execution_available"] is False
    assert report["options_execution_available"] is False
    assert report["leverage_execution_available"] is False
    assert report["live_trading_enabled"] is False
    assert report["blocked_reasons"]


def test_derivatives_risk_estimate_is_capped_and_paper_only() -> None:
    estimate = DerivativesRiskGuard().estimate(
        symbol="BTCUSDT",
        instrument="FUTURES",
        notional_usdt=1000,
        leverage=20,
        adverse_move_pct=10,
    )
    assert estimate["notional_usdt"] == 250.0
    assert estimate["leverage"] == 3.0
    assert estimate["allowed_for_live_execution"] is False
    assert estimate["safety_notes"]
