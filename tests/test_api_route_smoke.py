from pathlib import Path

from trading_os.api.dependencies import set_backend
from trading_os.api.routes import control, monitor, settings, status
from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend


def test_status_routes_return_safe_paper_mode_payloads(tmp_path: Path) -> None:
    backend = _backend(tmp_path)
    set_backend(backend)

    bot = status.bot_status()
    readiness = status.binance_readiness()
    shutdown = status.shutdown_status()
    runtime = status.runtime_status()

    for response in [bot, readiness, shutdown, runtime]:
        assert response["success"] is True
        assert response["errors"] == []

    assert bot["data"]["trading_mode"] == "paper"
    assert bot["data"]["live_trading_enabled"] is False
    assert readiness["data"]["ready"] is True
    assert shutdown["data"]["accepts_new_trades"] is True


def test_control_routes_keep_live_trading_disabled(tmp_path: Path) -> None:
    backend = _backend(tmp_path)
    set_backend(backend)

    start = control.start_runtime()
    pause = control.pause_new_trades()
    resume = control.resume_paper_trades()
    stop = control.stop_graceful()

    for response in [start, pause, resume, stop]:
        assert response["success"] is True
        assert response["errors"] == []

    assert backend.config.enable_live_trading is False
    assert backend.intent_layer.live_enabled is False


def test_monitor_routes_return_empty_safe_defaults(tmp_path: Path) -> None:
    backend = _backend(tmp_path)
    set_backend(backend)

    live = monitor.paper_live_monitor()
    summary = monitor.paper_scan_summary()
    paper_24h = monitor.paper_24h_status()

    assert live["success"] is True
    assert summary["success"] is True
    assert paper_24h["success"] is True
    assert live["data"]["live_trading_enabled"] is False
    assert live["data"]["public_data_only"] is True
    assert summary["data"]["live_trading_enabled"] is False
    assert summary["data"]["public_data_only"] is True
    assert paper_24h["data"]["window_hours"] == 24
    assert paper_24h["data"]["live_trading_enabled"] is False
    assert paper_24h["data"]["public_data_only"] is True


def test_security_route_includes_post_quantum_ready_policy(tmp_path: Path) -> None:
    backend = _backend(tmp_path)
    set_backend(backend)

    response = settings.get_security()

    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["withdrawals_supported"] is False
    pq = response["data"]["post_quantum_security"]
    assert pq["posture"] == "POST_QUANTUM_READY_DESIGN"
    assert pq["quantum_proof_claimed"] is False
    assert pq["app_contains_binance_secrets"] is False


def _backend(tmp_path: Path) -> TradingOSBackend:
    return TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
