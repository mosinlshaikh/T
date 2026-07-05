from __future__ import annotations

from dataclasses import asdict

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import fail, ok
from trading_os.market.live_public_data import BinancePublicMarketDataClient
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

    client = BinancePublicMarketDataClient()
    try:
        bundle = client.fetch_bundle(symbol=symbol, timeframe=timeframe)
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

    backend.market_data.ingest_rest_snapshot(bundle.snapshot)
    backend.candle_engine.collect(bundle.candles)
    backend.order_book_engine.update_snapshot(bundle.order_book)
    backend.audit_logger.log_market_snapshot(
        {
            "symbol": bundle.symbol,
            "timeframe": bundle.timeframe.value,
            "price": bundle.snapshot.price,
            "volume_24h": bundle.snapshot.volume_24h,
            "source": bundle.snapshot.source,
            "candles": len(bundle.candles),
            "order_book_bids": len(bundle.order_book.bids),
            "order_book_asks": len(bundle.order_book.asks),
            "whale_trades": len(bundle.whale_trades),
            "news_items": len(bundle.news_items),
            "public_data_only": True,
        }
    )

    pipeline_input = client.build_pipeline_input(
        bundle=bundle,
        account_balance=backend.portfolio.usdt_balance,
        current_exposure=backend.portfolio.exposure(),
        trade_notional_usdt=min(max(trade_notional_usdt, 10.0), 250.0),
    )
    result = backend.decision_to_trade_pipeline.run(pipeline_input, bundle.evidence)

    open_positions = [asdict(item) for item in backend.portfolio.open_positions.values()]
    return ok(
        {
            "symbol": result.symbol,
            "timeframe": result.timeframe.value,
            "status": result.status,
            "reason": result.reason,
            "decision": {
                "action": result.decision.action.value,
                "confidence": result.decision.confidence,
                "verified_decision": result.decision.verified_decision,
                "rejection_reason": result.decision.rejection_reason,
                "missing_data": result.decision.missing_data,
                "conflicts": result.decision.conflict_signals,
                "evidence_count": len(result.decision.evidence),
            },
            "market": {
                "price": bundle.snapshot.price,
                "candles": len(bundle.candles),
                "order_book_bids": len(bundle.order_book.bids),
                "order_book_asks": len(bundle.order_book.asks),
                "whale_trades": len(bundle.whale_trades),
                "news_items": len(bundle.news_items),
            },
            "execution_intent": asdict(result.execution_intent) if result.execution_intent else None,
            "paper_fill": asdict(result.paper_fill) if result.paper_fill else None,
            "open_positions": open_positions,
            "live_trading_enabled": False,
            "public_data_only": True,
        },
        "Live-market paper demo completed safely.",
        warnings=bundle.warnings,
    )
