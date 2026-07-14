from datetime import datetime, timedelta, timezone

from trading_os.reports.statement import StatementEngine


class FakeRepository:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.closed = [
            {
                "position_id": "win",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "status": "CLOSED",
                "closed_at": (now - timedelta(hours=2)).isoformat(),
                "realized_pnl": 4.25,
            },
            {
                "position_id": "old",
                "symbol": "ETHUSDT",
                "side": "BUY",
                "status": "CLOSED",
                "closed_at": (now - timedelta(hours=30)).isoformat(),
                "realized_pnl": 99.0,
            },
            {
                "position_id": "loss",
                "symbol": "SOLUSDT",
                "side": "BUY",
                "status": "CLOSED",
                "closed_at": (now - timedelta(hours=1)).isoformat(),
                "realized_pnl": -1.25,
            },
        ]
        self.journal = []
        self.open_positions = [{"position_id": "open"}]

    def list_closed_positions(self):
        return self.closed

    def list_trade_journal(self, limit=1000):
        return self.journal

    def list_open_positions(self):
        return self.open_positions


def test_statement_engine_uses_selected_window_and_pnl() -> None:
    statement = StatementEngine(FakeRepository()).build(hours=18)
    assert statement["window_hours"] == 18
    assert statement["realized_pnl"] == 3.0
    assert statement["gross_profit"] == 4.25
    assert statement["gross_loss"] == -1.25
    assert statement["open_positions"] == 1
    assert statement["closed_positions"] == 2
    assert statement["winning_trades"] == 1
    assert statement["losing_trades"] == 1
    assert statement["win_rate_pct"] == 50.0
    assert all(item["passed"] for item in statement["safety_checks"])


def test_statement_engine_default_is_daily_24h() -> None:
    statement = StatementEngine(FakeRepository()).build()
    assert statement["window_hours"] == 24
