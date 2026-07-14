from pathlib import Path

from trading_os.api.dependencies import set_backend
from trading_os.api.routes.control import (
    manual_paper_demo_close_market,
    manual_paper_demo_open,
    manual_paper_demo_simulate_stop_loss,
)
from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend


def test_manual_paper_demo_respects_kill_switch(tmp_path: Path) -> None:
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    backend.kill_switch.activate("test")
    set_backend(backend)
    response = manual_paper_demo_open()
    assert response["success"] is False
    assert response["message"] == "KILL_SWITCH_ACTIVE"


def test_manual_paper_demo_close_requires_open_position(tmp_path: Path) -> None:
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    set_backend(backend)
    response = manual_paper_demo_close_market()
    assert response["success"] is False
    assert response["message"] == "NO_OPEN_PAPER_POSITION"


def test_manual_paper_demo_can_close_persisted_position(tmp_path: Path) -> None:
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    backend.repository.save_open_position(
        {
            "position_id": "paper-1",
            "symbol": "BTCUSDT",
            "quantity": 0.01,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 110.0,
            "status": "OPEN",
        }
    )
    set_backend(backend)
    response = manual_paper_demo_simulate_stop_loss()
    assert response["success"] is True
    assert response["data"]["status"] == "PAPER_CLOSED"
    assert response["data"]["exit_type"] == "STOP_LOSS"
    assert backend.repository.list_open_positions() == []
