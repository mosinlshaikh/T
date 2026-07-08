from trading_os.db.repository import TradingOSRepository
from trading_os.db.storage import SQLiteStorage
from trading_os.learning.local_ai_engine import LocalAIMarketKingEngine


def test_local_ai_returns_insufficient_data_without_evidence(tmp_path) -> None:
    repository = TradingOSRepository(SQLiteStorage(f"sqlite:///{tmp_path / 'empty.sqlite3'}"))
    snapshot = LocalAIMarketKingEngine(repository).snapshot()

    assert snapshot.status == "insufficient_data"
    assert snapshot.auto_strategy_change is False
    assert snapshot.live_trading_impact is False
    assert "No Data = No Trade" in snapshot.guardrails


def test_local_ai_scores_persisted_paper_evidence_only(tmp_path) -> None:
    repository = TradingOSRepository(SQLiteStorage(f"sqlite:///{tmp_path / 'evidence.sqlite3'}"))
    repository.save_ai_decision(
        {
            "action": "HOLD",
            "confidence": 0.62,
            "symbol": "BTCUSDT",
            "evidence": [{"id": "candle-1"}],
        }
    )
    repository.save_strategy_signal(
        {"signal": "candle_structure_strategy", "confidence": 0.61, "source": "paper"}
    )
    repository.save_market_intelligence_snapshot({"symbol": "BTCUSDT", "source": "paper"})

    snapshot = LocalAIMarketKingEngine(repository).snapshot()

    assert snapshot.status == "ok"
    assert snapshot.learning_mode == "paper_only_local_ai"
    assert snapshot.action_distribution["HOLD"] == 1
    assert snapshot.confidence_profile["average"] == 0.62
    assert snapshot.strategy_scores["candle"]["status"] == "evidence_based"
    assert snapshot.auto_strategy_change is False
    assert snapshot.live_trading_impact is False
