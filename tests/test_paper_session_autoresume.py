from types import SimpleNamespace

from trading_os.runtime.paper_session_scheduler import PaperSessionScheduler


class FakeRepository:
    def __init__(self) -> None:
        self.settings = {}

    def save_settings(self, key, value):
        self.settings[key] = dict(value)

    def get_settings(self, key):
        return self.settings.get(key)


class FakeAudit:
    def __init__(self) -> None:
        self.events = []

    def log(self, event_type, payload):
        self.events.append((event_type, payload))

    def log_skipped_trade(self, payload):
        self.events.append(("skipped_trade", payload))


class FakePaperAutoTrader:
    def scan_once(self, symbols=None, timeframe="5m", trade_notional_usdt=50.0):
        return {
            "symbols": symbols or [],
            "timeframe": timeframe,
            "results": [],
            "errors": [],
            "best_candidate": {},
            "live_trading_enabled": False,
            "public_data_only": True,
            "trade_notional_usdt": trade_notional_usdt,
        }


def fake_backend(repository=None):
    return SimpleNamespace(
        config=SimpleNamespace(enable_live_trading=False),
        kill_switch=SimpleNamespace(active=False),
        repository=repository or FakeRepository(),
        audit_logger=FakeAudit(),
        paper_auto_trader=FakePaperAutoTrader(),
    )


def test_paper_session_start_and_stop_persist_desired_state() -> None:
    backend = fake_backend()
    scheduler = PaperSessionScheduler(backend=backend, min_interval_seconds=999)

    started = scheduler.start(symbols=["BTCUSDT"], interval_seconds=999)
    assert started["running"] is True
    assert started["auto_resume_enabled"] is True
    assert backend.repository.get_settings("paper_session")["enabled"] is True
    assert backend.repository.get_settings("paper_session")["live_trading_enabled"] is False

    stopped = scheduler.stop()
    assert stopped["running"] is False
    assert stopped["auto_resume_enabled"] is False
    assert backend.repository.get_settings("paper_session")["enabled"] is False


def test_paper_session_auto_resume_uses_persisted_safe_settings() -> None:
    repository = FakeRepository()
    repository.save_settings(
        "paper_session",
        {
            "enabled": True,
            "symbols": ["BTCUSDT", "ETHUSDT"],
            "timeframe": "5m",
            "interval_seconds": 999,
            "trade_notional_usdt": 50,
            "live_trading_enabled": False,
        },
    )
    backend = fake_backend(repository=repository)
    scheduler = PaperSessionScheduler(backend=backend, min_interval_seconds=999)

    status = scheduler.auto_resume_if_configured()

    assert status["running"] is True
    assert status["auto_resume_enabled"] is True
    assert status["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert status["live_trading_enabled"] is False
    assert repository.get_settings("paper_session")["enabled"] is True
    scheduler.stop()
