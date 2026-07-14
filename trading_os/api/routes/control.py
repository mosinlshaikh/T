from __future__ import annotations

from datetime import datetime, timezone

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import fail, ok
from trading_os.execution.intent import ExecutionIntent, OrderIntentType
from trading_os.market.live_public_data import BinancePublicMarketDataClient
from trading_os.runtime.shutdown_engine import ShutdownState

router = APIRouter(prefix="/control", tags=["control"])


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


@router.post("/manual-paper-demo/open")
def manual_paper_demo_open(
    symbol: str = "BTCUSDT",
    trade_notional_usdt: float = 25.0,
) -> dict[str, object]:
    """Open a clearly labeled manual paper demo position.

    This endpoint is for APK walkthrough/testing only. It never places a real
    Binance order and does not bypass live trading safety rules.
    """

    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail(
            "LIVE_TRADING_BLOCKED", errors=["Manual paper demo cannot enable live trading."]
        )
    if backend.kill_switch.active:
        return fail("KILL_SWITCH_ACTIVE", errors=["Emergency stop is active."])
    if not backend.shutdown_engine.accepts_new_trades:
        return fail("SHUTDOWN_REQUESTED", errors=["New paper demo trades are blocked."])

    safe_notional = min(max(float(trade_notional_usdt), 10.0), 100.0)
    try:
        bundle = BinancePublicMarketDataClient().fetch_bundle(
            symbol=symbol,
            timeframe="5m",
            candle_limit=20,
            order_book_limit=10,
            trade_limit=10,
        )
    except Exception as exc:
        return ok(
            {
                "status": "SKIP",
                "symbol": symbol.upper(),
                "reason": "Public market data unavailable; manual paper demo skipped safely.",
                "error": exc.__class__.__name__,
                "live_trading_enabled": False,
                "public_data_only": True,
            },
            "Manual paper demo skipped safely.",
            warnings=["No real order was sent."],
        )

    price = float(bundle.snapshot.price)
    quantity = round(safe_notional / price, 8)
    stop_loss = round(price * 0.99, 8)
    take_profit = round(price * 1.015, 8)
    intent = ExecutionIntent(
        symbol=bundle.symbol,
        side="BUY",
        quantity=quantity,
        stop_loss=stop_loss,
        take_profit=take_profit,
        reason="MANUAL PAPER DEMO: user-requested paper-only walkthrough trade.",
        evidence_ids=["manual-paper-demo", bundle.snapshot.source],
        risk_approval_id="manual-paper-demo-risk-capped",
        intent_type=OrderIntentType.MARKET_BUY,
        live_enabled=False,
    )
    fill = backend.paper_simulator.open_trade(intent, fill_price=price)
    backend.audit_logger.log(
        "manual_paper_demo_open",
        {
            "symbol": fill.symbol,
            "position_id": fill.position_id,
            "quantity": fill.quantity,
            "fill_price": fill.fill_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "notional_usdt": safe_notional,
            "reason": intent.reason,
            "live_trading_enabled": False,
            "public_data_only": True,
        },
    )
    return ok(
        {
            "status": "PAPER_OPEN",
            "symbol": fill.symbol,
            "position_id": fill.position_id,
            "side": fill.side,
            "quantity": fill.quantity,
            "fill_price": fill.fill_price,
            "fee": fill.fee,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reason": intent.reason,
            "live_trading_enabled": False,
            "public_data_only": True,
            "manual_demo": True,
        },
        "Manual paper demo position opened.",
        warnings=["Paper mode only. This is not an AI trade and no real Binance order was sent."],
    )


def _latest_memory_position_id() -> str | None:
    backend = get_backend()
    if not backend.portfolio.open_positions:
        return None
    return next(reversed(backend.portfolio.open_positions))


def _latest_persisted_position() -> dict[str, object] | None:
    backend = get_backend()
    positions = backend.repository.list_open_positions()
    return positions[-1] if positions else None


def _manual_exit_intent(
    position_id: str, intent_type: OrderIntentType, reason: str
) -> ExecutionIntent:
    backend = get_backend()
    position = backend.portfolio.open_positions[position_id]
    return ExecutionIntent(
        symbol=position.symbol,
        side="SELL",
        quantity=position.quantity,
        stop_loss=position.stop_loss,
        take_profit=position.take_profit,
        reason=reason,
        evidence_ids=["manual-paper-demo-exit"],
        risk_approval_id="manual-paper-demo-exit-risk-capped",
        intent_type=intent_type,
        live_enabled=False,
    )


def _paper_exit_payload(fill: object, reason: str, exit_type: str) -> dict[str, object]:
    return {
        "status": "PAPER_CLOSED",
        "exit_type": exit_type,
        "symbol": fill.symbol,
        "position_id": fill.position_id,
        "side": fill.side,
        "quantity": fill.quantity,
        "fill_price": fill.fill_price,
        "fee": fill.fee,
        "reason": reason,
        "live_trading_enabled": False,
        "public_data_only": True,
        "manual_demo": True,
    }


def _paper_exit_payload_from_position(
    position: dict[str, object],
    fill_price: float,
    fee: float,
    realized_pnl: float,
    reason: str,
    exit_type: str,
) -> dict[str, object]:
    return {
        "status": "PAPER_CLOSED",
        "exit_type": exit_type,
        "symbol": str(position.get("symbol", "")).upper(),
        "position_id": str(position.get("position_id", "")),
        "side": "SELL",
        "quantity": float(position.get("quantity", 0.0) or 0.0),
        "fill_price": fill_price,
        "fee": round(fee, 8),
        "realized_pnl": round(realized_pnl, 8),
        "reason": reason,
        "live_trading_enabled": False,
        "public_data_only": True,
        "manual_demo": True,
    }


def _close_persisted_position(
    position: dict[str, object],
    fill_price: float,
    reason: str,
    exit_type: str,
) -> dict[str, object]:
    backend = get_backend()
    quantity = float(position.get("quantity", 0.0) or 0.0)
    entry_price = float(position.get("entry_price", 0.0) or 0.0)
    fee = quantity * fill_price * backend.paper_simulator.fee_rate
    realized_pnl = (fill_price - entry_price) * quantity - fee
    closed = {
        **position,
        "closed_at": utc_now(),
        "realized_pnl": round(realized_pnl, 8),
        "status": "CLOSED",
    }
    backend.repository.close_position(closed)
    backend.repository.save_trade_journal_entry(
        {
            "symbol": str(position.get("symbol", "")).upper(),
            "action": "PAPER_CLOSED",
            "mode": "paper",
            "reason": reason,
            "realized_pnl": round(realized_pnl, 8),
            "created_at": utc_now(),
            "trade_id": str(position.get("position_id", "")),
        }
    )
    payload = _paper_exit_payload_from_position(
        position, fill_price, fee, realized_pnl, reason, exit_type
    )
    backend.audit_logger.log("manual_paper_demo_close", payload)
    return payload


@router.post("/manual-paper-demo/close-market")
def manual_paper_demo_close_market() -> dict[str, object]:
    backend = get_backend()
    position_id = _latest_memory_position_id()
    persisted_position = None
    if position_id is None:
        persisted_position = _latest_persisted_position()
    if position_id is None and persisted_position is None:
        return fail("NO_OPEN_PAPER_POSITION", errors=["No active paper position exists."])
    position = (
        backend.portfolio.open_positions[position_id]
        if position_id is not None
        else persisted_position
    )
    try:
        bundle = BinancePublicMarketDataClient().fetch_bundle(
            symbol=(
                position.symbol
                if position_id is not None
                else str(position.get("symbol", "BTCUSDT"))
            ),
            timeframe="5m",
            candle_limit=5,
            order_book_limit=5,
            trade_limit=5,
        )
        price = float(bundle.snapshot.price)
    except Exception:
        price = (
            float(position.entry_price)
            if position_id is not None
            else float(position.get("entry_price", 0.0) or 0.0)
        )
    reason = "MANUAL PAPER DEMO: user-requested paper-only market close."
    if position_id is not None:
        intent = _manual_exit_intent(position_id, OrderIntentType.MARKET_SELL, reason)
        fill = backend.paper_simulator.close_trade(position_id, intent, price)
        payload = _paper_exit_payload(fill, reason, "MARKET_CLOSE")
        backend.audit_logger.log("manual_paper_demo_close", payload)
    else:
        payload = _close_persisted_position(position, price, reason, "MARKET_CLOSE")
    return ok(
        payload,
        "Manual paper demo position closed.",
        warnings=["Paper mode only. No real Binance order was sent."],
    )


@router.post("/manual-paper-demo/simulate-stop-loss")
def manual_paper_demo_simulate_stop_loss() -> dict[str, object]:
    backend = get_backend()
    position_id = _latest_memory_position_id()
    persisted_position = None
    if position_id is None:
        persisted_position = _latest_persisted_position()
    if position_id is None and persisted_position is None:
        return fail("NO_OPEN_PAPER_POSITION", errors=["No active paper position exists."])
    reason = "MANUAL PAPER DEMO: stop-loss simulation."
    if position_id is not None:
        intent = _manual_exit_intent(position_id, OrderIntentType.STOP_LOSS, reason)
        fill = backend.paper_simulator.simulate_stop_loss_hit(position_id, intent)
        payload = _paper_exit_payload(fill, reason, "STOP_LOSS")
        backend.audit_logger.log("manual_paper_demo_stop_loss", payload)
    else:
        payload = _close_persisted_position(
            persisted_position,
            float(persisted_position.get("stop_loss", 0.0) or 0.0),
            reason,
            "STOP_LOSS",
        )
    return ok(
        payload,
        "Manual paper stop-loss simulation completed.",
        warnings=["Paper mode only. No real Binance order was sent."],
    )


@router.post("/manual-paper-demo/simulate-take-profit")
def manual_paper_demo_simulate_take_profit() -> dict[str, object]:
    backend = get_backend()
    position_id = _latest_memory_position_id()
    persisted_position = None
    if position_id is None:
        persisted_position = _latest_persisted_position()
    if position_id is None and persisted_position is None:
        return fail("NO_OPEN_PAPER_POSITION", errors=["No active paper position exists."])
    reason = "MANUAL PAPER DEMO: take-profit simulation."
    if position_id is not None:
        intent = _manual_exit_intent(position_id, OrderIntentType.TAKE_PROFIT, reason)
        fill = backend.paper_simulator.simulate_take_profit_hit(position_id, intent)
        payload = _paper_exit_payload(fill, reason, "TAKE_PROFIT")
        backend.audit_logger.log("manual_paper_demo_take_profit", payload)
    else:
        payload = _close_persisted_position(
            persisted_position,
            float(persisted_position.get("take_profit", 0.0) or 0.0),
            reason,
            "TAKE_PROFIT",
        )
    return ok(
        payload,
        "Manual paper take-profit simulation completed.",
        warnings=["Paper mode only. No real Binance order was sent."],
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


@router.post("/paper-auto-trader/scan")
def paper_auto_trader_scan(
    symbols: str = "BTCUSDT,ETHUSDT",
    timeframe: str = "5m",
    trade_notional_usdt: float = 50.0,
    all_usdt_symbols: bool = False,
) -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail("LIVE_TRADING_BLOCKED", errors=["Paper scanner cannot enable live trading."])
    if backend.kill_switch.active:
        return fail("KILL_SWITCH_ACTIVE", errors=["Emergency stop is active."])
    safe_symbols = [item.strip().upper() for item in symbols.split(",") if item.strip()]
    payload = backend.paper_auto_trader.scan_once(
        symbols=safe_symbols,
        timeframe=timeframe,
        trade_notional_usdt=trade_notional_usdt,
        all_usdt_symbols=all_usdt_symbols,
    )
    return ok(
        payload,
        "Multi-symbol paper scanner completed.",
        warnings=["Paper mode only. No real Binance orders are placed."],
    )


@router.post("/paper-auto-trader/scan-all")
def paper_auto_trader_scan_all(
    timeframe: str = "5m",
    trade_notional_usdt: float = 50.0,
    max_symbols: int = 5,
) -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail(
            "LIVE_TRADING_BLOCKED", errors=["All-coin paper scanner cannot enable live trading."]
        )
    if backend.kill_switch.active:
        return fail("KILL_SWITCH_ACTIVE", errors=["Emergency stop is active."])
    payload = backend.paper_auto_trader.scan_once(
        symbols=None,
        timeframe=timeframe,
        trade_notional_usdt=trade_notional_usdt,
        all_usdt_symbols=True,
        max_symbols_override=max_symbols,
    )
    return ok(
        payload,
        "All active Binance Spot USDT paper scanner completed in a safe batch.",
        warnings=[
            "Paper mode only. No real Binance orders are placed.",
            "Full universe is discovered; scanning is batch-limited for rate-limit safety.",
        ],
    )


@router.post("/paper-auto-trader/start")
def start_paper_auto_trader(
    symbols: str = "BTCUSDT",
    timeframe: str = "5m",
    interval_seconds: int = 60,
    trade_notional_usdt: float = 50.0,
    all_usdt_symbols: bool = False,
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
            all_usdt_symbols=all_usdt_symbols,
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


@router.post("/paper-session/start")
def start_paper_session(
    symbols: str = "BTCUSDT,ETHUSDT,SOLUSDT",
    timeframe: str = "5m",
    interval_seconds: int = 300,
    trade_notional_usdt: float = 50.0,
) -> dict[str, object]:
    backend = get_backend()
    if backend.config.enable_live_trading:
        return fail("LIVE_TRADING_BLOCKED", errors=["Paper session cannot enable live trading."])
    if backend.kill_switch.active:
        return fail("KILL_SWITCH_ACTIVE", errors=["Emergency stop is active."])
    safe_symbols = [item.strip().upper() for item in symbols.split(",") if item.strip()]
    return ok(
        backend.paper_session_scheduler.start(
            symbols=safe_symbols,
            timeframe=timeframe,
            interval_seconds=interval_seconds,
            trade_notional_usdt=trade_notional_usdt,
        ),
        "24x7 paper session scheduler started.",
        warnings=["Paper mode only. No real Binance orders are placed."],
    )


@router.post("/paper-session/stop")
def stop_paper_session() -> dict[str, object]:
    backend = get_backend()
    return ok(backend.paper_session_scheduler.stop(), "Paper session scheduler stopped.")


@router.get("/paper-session/status")
def paper_session_status() -> dict[str, object]:
    backend = get_backend()
    backend.paper_session_scheduler.auto_resume_if_configured()
    return ok(backend.paper_session_scheduler.status(), "Paper session scheduler status loaded.")
