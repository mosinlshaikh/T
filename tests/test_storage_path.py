from pathlib import Path

from trading_os.db.storage import sqlite_path


def test_sqlite_data_path_stays_relative_by_default(monkeypatch):
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT_ID", raising=False)
    monkeypatch.delenv("RAILWAY_PROJECT_ID", raising=False)
    monkeypatch.delenv("RAILWAY_SERVICE_ID", raising=False)

    assert sqlite_path("sqlite:///data/trading_os.sqlite3") == Path("data/trading_os.sqlite3")


def test_sqlite_data_path_uses_railway_volume_when_running_on_railway(monkeypatch):
    monkeypatch.setenv("RAILWAY_SERVICE_ID", "service-id")

    assert sqlite_path("sqlite:///data/trading_os.sqlite3") == Path("/data/trading_os.sqlite3")
