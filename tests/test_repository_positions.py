from pathlib import Path

from trading_os.db.repository import TradingOSRepository
from trading_os.db.storage import SQLiteStorage


def test_closed_positions_are_not_listed_as_open(tmp_path: Path) -> None:
    repository = TradingOSRepository(SQLiteStorage(f"sqlite:///{tmp_path / 'trading.sqlite3'}"))
    position = {
        "position_id": "paper-1",
        "symbol": "BTCUSDT",
        "status": "OPEN",
    }
    closed = {**position, "status": "CLOSED"}

    repository.save_open_position(position)
    assert len(repository.list_open_positions()) == 1

    repository.close_position(closed)
    assert repository.list_open_positions() == []
    assert repository.list_closed_positions()[0]["position_id"] == "paper-1"
