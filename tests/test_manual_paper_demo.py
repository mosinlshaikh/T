from pathlib import Path

from trading_os.api.dependencies import set_backend
from trading_os.api.routes.control import manual_paper_demo_open
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
