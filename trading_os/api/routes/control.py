from __future__ import annotations

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import fail, ok
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


@router.post("/run-live-market-paper-demo")
def run_live_market_paper_demo(
    symbol: str = "BTCUSDT",
    timeframe: str = "5m",
    trade_notional_usdt: float = 50.0,
) -> dict[str, object]:
    """Run a safe public-market paper demo.

    This reads unauthenticated public market data only. It never sends private
    Binance requests, never places real orders, and remains paper-mode only.
    """

    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail(
            "LIVE_TRADING_BLOCKED",
            errors=["Live trading must remain disabled for this demo endpoint."],
        )
    if backend.kill_switch.active:
        return fail(
            "KILL_SWITCH_ACTIVE",
            errors=["Emergency kill switch is active; no paper demo trade is opened."],
        )

    try:
        auto_result = backend.paper_auto_trader.run_once(
            symbol=symbol,
            timeframe=timeframe,
            trade_notional_usdt=trade_notional_usdt,
        )
    except Exception as exc:
        safe_reason = "Public market data unavailable; paper demo skipped safely."
        backend.audit_logger.log_skipped_trade(
            {"symbol": symbol.upper(), "reason": safe_reason, "error": exc.__class__.__name__}
        )
        return ok(
            {
                "status": "SKIP",
                "symbol": symbol.upper(),
                "reason": safe_reason,
                "live_trading_enabled": False,
                "public_data_only": True,
            },
            "Live-market paper demo skipped safely.",
            warnings=[safe_reason],
        )

    return ok(
        {
            "symbol": auto_result.symbol,
            "timeframe": auto_result.timeframe,
            "status": auto_result.status,
            "reason": auto_result.reason,
            "decision": {
                "action": auto_result.action,
                "confidence": auto_result.confidence,
            },
            "paper_fill_id": auto_result.paper_fill_id,
            "auto_paper_trader": backend.paper_auto_trader.status(),
            "live_trading_enabled": False,
            "public_data_only": True,
        },
        "Live-market paper demo completed safely.",
    )


@router.post("/paper-auto-trader/tick")
def paper_auto_trader_tick(
    symbol: str = "BTCUSDT",
    timeframe: str = "5m",
    trade_notional_usdt: float = 50.0,
) -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail(
            "LIVE_TRADING_BLOCKED", errors=["Paper auto trader cannot enable live trading."]
        )
    if backend.kill_switch.active:
        return fail("KILL_SWITCH_ACTIVE", errors=["Emergency stop is active."])
    try:
        result = backend.paper_auto_trader.run_once(symbol, timeframe, trade_notional_usdt)
    except Exception as exc:
        return ok(
            {
                "status": "SKIP",
                "symbol": symbol.upper(),
                "reason": "Paper auto trader tick skipped safely.",
                "error": exc.__class__.__name__,
                "live_trading_enabled": False,
            },
            "Paper auto trader tick skipped safely.",
            warnings=["No real order was sent."],
        )
    return ok(result.__dict__, "Paper auto trader tick completed.")


@router.post("/paper-auto-trader/start")
def start_paper_auto_trader(
    symbols: str = "BTCUSDT",
    timeframe: str = "5m",
    interval_seconds: int = 60,
    trade_notional_usdt: float = 50.0,
) -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail(
            "LIVE_TRADING_BLOCKED", errors=["Paper auto trader cannot enable live trading."]
        )
    safe_symbols = [item.strip().upper() for item in symbols.split(",") if item.strip()]
    return ok(
        backend.paper_auto_trader.start(
            symbols=safe_symbols or ["BTCUSDT"],
            timeframe=timeframe,
            interval_seconds=interval_seconds,
            trade_notional_usdt=trade_notional_usdt,
        ),
        "Paper auto trader started.",
        warnings=["Paper mode only. No real Binance orders are placed."],
    )


@router.post("/paper-auto-trader/stop")
def stop_paper_auto_trader() -> dict[str, object]:
    backend = get_backend()
    return ok(backend.paper_auto_trader.stop(), "Paper auto trader stopped.")


@router.get("/paper-auto-trader/status")
def paper_auto_trader_status() -> dict[str, object]:
    backend = get_backend()
    return ok(backend.paper_auto_trader.status(), "Paper auto trader status loaded.")
