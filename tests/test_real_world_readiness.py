from trading_os.config import TradingOSConfig
from trading_os.db.repository import TradingOSRepository
from trading_os.db.storage import SQLiteStorage
from trading_os.learning.local_ai_engine import LocalAIMarketKingEngine
from trading_os.risk.risk_engine import RiskEngine
from trading_os.runtime.real_world_readiness import RealWorldReadinessGate, report_to_dict
from trading_os.security.api_key_vault import ApiKeyVaultDesign
from trading_os.security.kill_switch import EmergencyKillSwitch
from trading_os.security.permission_verifier import BinanceApiPermissionVerifier


def _gate(tmp_path, config: TradingOSConfig | None = None) -> RealWorldReadinessGate:
    repository = TradingOSRepository(SQLiteStorage(f"sqlite:///{tmp_path / 'rw.sqlite3'}"))
    return RealWorldReadinessGate(
        config=config or TradingOSConfig(),
        vault=ApiKeyVaultDesign(),
        permission_verifier=BinanceApiPermissionVerifier(),
        risk_engine=RiskEngine(),
        kill_switch=EmergencyKillSwitch(),
        local_ai=LocalAIMarketKingEngine(repository),
    )


def test_real_world_readiness_allows_paper_but_blocks_real_money(tmp_path) -> None:
    report = _gate(tmp_path).evaluate()

    assert report.ready_for_paper is True
    assert report.ready_for_real_money is False
    assert report.live_execution_available is False
    assert "must not place real Binance orders" in report.safety_statement


def test_manual_live_unlock_blocks_readiness(tmp_path) -> None:
    report = _gate(tmp_path, TradingOSConfig(manual_live_unlock=True)).evaluate()

    assert report.ready_for_paper is False
    assert report.ready_for_real_money is False
    assert any("Manual live unlock" in item for item in report.blockers)


def test_real_world_readiness_report_is_api_safe(tmp_path) -> None:
    payload = report_to_dict(_gate(tmp_path).evaluate())

    assert payload["live_execution_available"] is False
    assert payload["ready_for_real_money"] is False
    assert payload["checks"]
