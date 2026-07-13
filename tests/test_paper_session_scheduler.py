from types import SimpleNamespace

from trading_os.runtime.paper_session_scheduler import PaperSessionScheduler


class FakeAudit:
    def __init__(self) -> None:
        self.events = []

    def log(self, event_type, payload):
        self.events.append((event_type, payload))

    def log_skipped_trade(self, payload):
        self.events.append(("skipped_trade", payload))


class FakeScanner:
    def __init__(self) -> None:
        self.calls = 0

    def scan_once(self, symbols=None, timeframe="5m", trade_notional_usdt=50.0):
        self.calls += 1
        return {
            "symbols": symbols or ["BTCUSDT"],
            "timeframe": timeframe,
            "results": [],
            "errors": [],
            "best_candidate": None,
            "live_trading_enabled": False,
            "public_data_only": True,
        }


def fake_backend():
    return SimpleNamespace(
        config=SimpleNamespace(enable_live_trading=False),
        kill_switch=SimpleNamespace(active=False),
        audit_logger=FakeAudit(),
        paper_auto_trader=FakeScanner(),
    )


def test_paper_session_scheduler_starts_scans_and_stops() -> None:
    backend = fake_backend()
    scheduler = PaperSessionScheduler(backend, min_interval_seconds=1)

    status = scheduler.start(["btcusdt", "ETHUSDT"], interval_seconds=1)
    scheduler._stop.wait(0.2)
    stopped = scheduler.stop()

    assert status["running"] is True
    assert stopped["running"] is False
    assert stopped["live_trading_enabled"] is False
    assert backend.paper_auto_trader.calls >= 1
    assert any(event[0] == "paper_session_started" for event in backend.audit_logger.events)


def test_paper_session_scheduler_blocks_live_trading() -> None:
    backend = fake_backend()
    backend.config.enable_live_trading = True
    scheduler = PaperSessionScheduler(backend)

    try:
        scheduler.start()
    except RuntimeError as exc:
        assert "live trading" in str(exc)
    else:
        raise AssertionError("scheduler should block live trading")
