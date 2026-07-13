from pathlib import Path

from trading_os.api.dependencies import set_backend
from trading_os.api.routes.monitor import candle_detail
from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend


def test_candle_detail_missing_data_is_safe() -> None:
    response = candle_detail(symbol="BTCUSDT", timeframe="5m", limit=40)
    assert response["success"] is True
    assert response["data"]["live_trading_enabled"] is False
    assert response["data"]["public_data_only"] is True
    assert "decision_rule" in response["data"]


def test_candle_detail_reads_persisted_archive(tmp_path: Path) -> None:
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    backend.repository.save_market_intelligence_snapshot(
        {
            "type": "candle_archive",
            "symbol": "BTCUSDT",
            "timeframe": "5m",
            "candles": [
                {
                    "symbol": "BTCUSDT",
                    "timeframe": "5m",
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 10.0,
                    "start_time_ms": 1,
                    "end_time_ms": 2,
                }
            ],
        }
    )
    set_backend(backend)
    response = candle_detail(symbol="BTCUSDT", timeframe="5m", limit=5)
    assert response["data"]["source"] == "persisted_candle_archive"
    assert response["data"]["latest_close"] == 100.5
    assert response["data"]["missing_data"] == []
