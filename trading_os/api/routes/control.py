from __future__ import annotations

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.runtime.shutdown_engine import ShutdownState

router = APIRouter(prefix="/control", tags=["control"])


@router.post("/start")
def start_runtime() -> dict[str, object]:
    backend = get_backend()
    state = backend.runtime_supervisor.start()
    return ok({"state": state.value}, "Runtime start requested.")


@router.post("/stop-graceful")
def stop_graceful() -> dict[str, object]:
    backend = get_backend()
    state = backend.runtime_supervisor.request_stop(len(backend.portfolio.open_positions))
    return ok({"state": state.value}, "Graceful shutdown requested.")


@router.post("/emergency-stop")
def emergency_stop() -> dict[str, object]:
    backend = get_backend()
    state = backend.runtime_supervisor.emergency_stop("Emergency stop requested by API.")
    backend.kill_switch.activate("Emergency stop requested by API.")
    return ok({"state": state.value, "kill_switch_active": True}, "Emergency stop activated.")


@router.post("/restart-runtime")
def restart_runtime() -> dict[str, object]:
    backend = get_backend()
    backend.runtime_supervisor.request_stop(len(backend.portfolio.open_positions))
    state = backend.runtime_supervisor.boot()
    return ok({"state": state.value}, "Runtime restart requested.")


@router.post("/pause-new-trades")
def pause_new_trades() -> dict[str, object]:
    backend = get_backend()
    state = backend.shutdown_engine.request_shutdown(len(backend.portfolio.open_positions))
    return ok({"shutdown_state": state.value}, "New paper trades paused.")


@router.post("/resume-paper-trades")
def resume_paper_trades() -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return ok(
            {"resumed": False, "live_trading_enabled": False},
            "Live trading cannot be enabled.",
            warnings=["Live trading remains blocked."],
        )
    backend.shutdown_engine.state = ShutdownState.RUNNING
    backend.runtime_supervisor.healthy = True
    return ok({"resumed": True, "mode": backend.config.runtime_mode.value}, "Paper trades resumed.")
