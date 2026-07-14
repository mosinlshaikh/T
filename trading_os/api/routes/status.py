from __future__ import annotations

from trading_os.api.dependencies import get_backend, latest_audit_events, latest_decisions
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.learning.local_ai_engine import LocalAIMarketKingEngine
from trading_os.runtime.real_world_readiness import RealWorldReadinessGate, report_to_dict

router = APIRouter(prefix="/status", tags=["status"])


def _runtime_payload() -> dict[str, object]:
    backend = get_backend()
    return {
        "bot_state": backend.runtime_supervisor.state.value,
        "trading_mode": backend.config.runtime_mode.value,
        "live_trading_enabled": backend.config.enable_live_trading,
        "api_readiness_status": backend.permission_verifier.verify(
            backend.config, backend.api_vault
        ).status.value,
        "vault_status": backend.api_vault.health_report(),
        "supervisor_health": backend.runtime_supervisor.healthy,
        "last_heartbeat": backend.runtime_supervisor.last_heartbeat_at or "NOT_STARTED",
        "last_heartbeat_count": backend.runtime_supervisor.heartbeat_count,
        "failure_state": backend.runtime_supervisor.failure_state.value,
        "last_error": backend.runtime_supervisor.last_error,
    }


@router.get("/bot")
def bot_status() -> dict[str, object]:
    return ok(_runtime_payload(), "Bot status loaded.")


@router.get("/health")
def health_status() -> dict[str, object]:
    backend = get_backend()
    payload = backend.health()
    payload["latest_decisions"] = latest_decisions(limit=5)
    payload["latest_audit_events"] = latest_audit_events(limit=5)
    backend.audit_logger.log_health_snapshot(payload)
    return ok(payload, "Health status loaded.")


@router.get("/binance-readiness")
def binance_readiness() -> dict[str, object]:
    backend = get_backend()
    result = backend.permission_verifier.verify(backend.config, backend.api_vault)
    return ok(
        {"status": result.status.value, "ready": result.ready, "reasons": result.reasons},
        "Binance readiness loaded.",
    )


@router.get("/shutdown")
def shutdown_status() -> dict[str, object]:
    backend = get_backend()
    return ok(
        {
            "state": backend.shutdown_engine.state.value,
            "accepts_new_trades": backend.shutdown_engine.accepts_new_trades,
            "must_manage_active_trades": backend.shutdown_engine.must_manage_active_trades,
            "stop_loss_take_profit_must_remain_active": (
                backend.shutdown_engine.stop_loss_take_profit_must_remain_active
            ),
        },
        "Shutdown status loaded.",
    )


@router.get("/runtime")
def runtime_status() -> dict[str, object]:
    return ok(_runtime_payload(), "Runtime status loaded.")


@router.get("/real-world-readiness")
def real_world_readiness() -> dict[str, object]:
    backend = get_backend()
    gate = RealWorldReadinessGate(
        config=backend.config,
        vault=backend.api_vault,
        permission_verifier=backend.permission_verifier,
        risk_engine=backend.risk_engine,
        kill_switch=backend.kill_switch,
        local_ai=LocalAIMarketKingEngine(backend.repository),
    )
    return ok(
        report_to_dict(gate.evaluate()),
        "Real-world readiness report loaded. Real-money execution remains blocked.",
    )
