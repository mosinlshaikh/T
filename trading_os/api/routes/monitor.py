from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trading_os.api.dependencies import get_backend, latest_audit_events, latest_decisions
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok, redact_sensitive
from trading_os.market.candle_engine import Candle
from trading_os.market.timeframes import normalize_timeframe

router = APIRouter(prefix="/monitor", tags=["monitor"])


INTELLIGENCE_TYPES = {
    "candle_analysis",
    "order_book_analysis",
    "whale_analysis",
    "news_risk_analysis",
    "market_structure_analysis",
    "combined_signal_result",
    "missing_data",
    "conflict_reason",
}

INTELLIGENCE_LABELS = {
    "candle_analysis": "Candle",
    "order_book_analysis": "Order Book",
    "whale_analysis": "Whale",
    "news_risk_analysis": "News Risk",
    "market_structure_analysis": "Market Structure",
    "combined_signal_result": "Combined Signal",
    "missing_data": "Missing Data",
    "conflict_reason": "Conflict",
}


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload", event)
    return payload if isinstance(payload, dict) else {}


def _latest_by_type(events: list[dict[str, Any]], event_type: str) -> dict[str, Any] | None:
    for event in reversed(events):
        if event.get("event_type") == event_type:
            return _payload(event)
    return None


def _latest_decision_payload() -> dict[str, Any] | None:
    decisions = latest_decisions(limit=1)
    return decisions[-1] if decisions else None


@router.get("/paper-live")
def paper_live_monitor() -> dict[str, object]:
    backend = get_backend()
    events = latest_audit_events(limit=250)
    latest_decision = _latest_decision_payload()
    latest_market = _latest_by_type(events, "market_snapshot")
    latest_pipeline = _latest_by_type(events, "decision_to_trade_pipeline_result")
    latest_fill = _latest_by_type(events, "paper_order_fill")
    latest_intelligence = [
        {
            "event_type": event.get("event_type", ""),
            "created_at": event.get("created_at", ""),
            "payload": _payload(event),
        }
        for event in events
        if event.get("event_type") in INTELLIGENCE_TYPES
    ][-25:]
    audit_timeline = [
        {
            "event_type": event.get("event_type", ""),
            "created_at": event.get("created_at", ""),
            "payload": _payload(event),
        }
        for event in events[-50:]
    ]
    open_positions = backend.repository.list_open_positions() or [
        asdict(item) for item in backend.portfolio.open_positions.values()
    ]
    closed_positions = backend.repository.list_closed_positions() or [
        asdict(item) for item in backend.portfolio.closed_positions
    ]
    journal = backend.repository.list_trade_journal(limit=100) or [
        asdict(item) for item in backend.paper_simulator.journal.entries
    ]
    wallet = backend.portfolio.wallet_snapshot()
    payload = {
        "mode": backend.config.runtime_mode.value,
        "live_trading_enabled": False,
        "public_data_only": True,
        "withdrawals_supported": False,
        "latest_decision": latest_decision,
        "latest_market_snapshot": latest_market,
        "latest_pipeline_result": latest_pipeline,
        "latest_paper_fill": latest_fill,
        "open_positions": open_positions,
        "closed_positions": closed_positions[-50:],
        "paper_journal": journal[-100:],
        "paper_session": backend.paper_session_scheduler.status(),
        "portfolio": {
            "usdt_balance": wallet.usdt_balance,
            "reserved_capital": wallet.reserved_capital,
            "realized_pnl": wallet.realized_pnl,
            "unrealized_pnl": wallet.unrealized_pnl,
            "exposure": backend.portfolio.exposure(),
            "available_capital": backend.portfolio.available_capital(),
            "daily_pnl": backend.portfolio.daily_pnl(),
            "drawdown_pct": backend.portfolio.drawdown_pct(),
        },
        "market_intelligence": latest_intelligence,
        "audit_timeline": audit_timeline,
    }
    return ok(redact_sensitive(payload), "Live paper monitor loaded.")


def _evidence_item(event: dict[str, Any]) -> dict[str, object]:
    payload = _payload(event)
    event_type = str(event.get("event_type", "unknown"))
    signal = str(
        payload.get("signal")
        or payload.get("final_signal")
        or payload.get("status")
        or payload.get("action")
        or "unknown"
    )
    confidence = payload.get("confidence_score", payload.get("confidence", "unknown"))
    summary = str(
        payload.get("reason")
        or payload.get("summary")
        or payload.get("detail")
        or "Evidence unavailable."
    )
    missing_data = payload.get("missing_data", [])
    conflicts = payload.get("conflicts", payload.get("conflict_signals", []))
    return {
        "timestamp": event.get("created_at", payload.get("timestamp", "")),
        "layer": INTELLIGENCE_LABELS.get(event_type, event_type.replace("_", " ").title()),
        "event_type": event_type,
        "symbol": payload.get("symbol", ""),
        "signal": signal,
        "confidence": confidence,
        "summary": summary,
        "missing_data": missing_data if isinstance(missing_data, list) else [str(missing_data)],
        "conflicts": conflicts if isinstance(conflicts, list) else [str(conflicts)],
        "source": payload.get("source", event_type),
    }


@router.get("/market-evidence")
def market_evidence_feed() -> dict[str, object]:
    events = latest_audit_events(limit=300)
    evidence = [
        _evidence_item(event) for event in events if event.get("event_type") in INTELLIGENCE_TYPES
    ]
    payload = {
        "items": evidence[-50:],
        "live_trading_enabled": False,
        "public_data_only": True,
        "rule": "No Data = No Trade; No Proof = No Decision",
    }
    return ok(redact_sensitive(payload), "Market evidence feed loaded.")


def _safe_float(value: float) -> float:
    return round(float(value), 8)


def _candle_from_payload(payload: dict[str, Any]) -> Candle | None:
    try:
        return Candle(
            symbol=str(payload["symbol"]).upper(),
            timeframe=normalize_timeframe(str(payload["timeframe"])),
            open=float(payload["open"]),
            high=float(payload["high"]),
            low=float(payload["low"]),
            close=float(payload["close"]),
            volume=float(payload.get("volume", 0.0) or 0.0),
            start_time_ms=int(payload.get("start_time_ms", 0) or 0),
            end_time_ms=int(payload.get("end_time_ms", 0) or 0),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _persisted_candles(backend: Any, symbol: str, timeframe: str, limit: int) -> list[Candle]:
    snapshots = backend.repository.list_market_intelligence_snapshots(limit=200)
    for snapshot in reversed(snapshots):
        if snapshot.get("type") != "candle_archive":
            continue
        if str(snapshot.get("symbol", "")).upper() != symbol.upper():
            continue
        if str(snapshot.get("timeframe", "")).lower() != str(timeframe).lower():
            continue
        candles = [
            candle
            for candle in (_candle_from_payload(item) for item in snapshot.get("candles", []))
            if candle is not None
        ]
        if candles:
            return candles[-limit:]
    return []


@router.get("/candle-detail")
def candle_detail(
    symbol: str = "BTCUSDT", timeframe: str = "5m", limit: int = 40
) -> dict[str, object]:
    backend = get_backend()
    safe_limit = min(max(int(limit), 5), 100)
    candles = backend.candle_engine.by_timeframe(symbol.upper(), timeframe)[-safe_limit:]
    source = "memory_candle_engine"
    if not candles:
        candles = _persisted_candles(backend, symbol.upper(), timeframe, safe_limit)
        source = "persisted_candle_archive" if candles else "none"
    if not candles:
        payload = {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "candles": [],
            "trend": "unknown",
            "latest_close": None,
            "range_high": None,
            "range_low": None,
            "volume_total": 0.0,
            "missing_data": ["candles"],
            "source": source,
            "live_trading_enabled": False,
            "public_data_only": True,
            "decision_rule": "Missing candle data = SKIP",
        }
        return ok(payload, "Candle detail unavailable; missing candle data.")

    closes = [candle.close for candle in candles]
    trend = "range"
    if len(closes) >= 3 and closes[-1] > closes[-2] > closes[-3]:
        trend = "uptrend"
    elif len(closes) >= 3 and closes[-1] < closes[-2] < closes[-3]:
        trend = "downtrend"
    range_high = max(candle.high for candle in candles)
    range_low = min(candle.low for candle in candles)
    volume_total = sum(candle.volume for candle in candles)
    payload = {
        "symbol": symbol.upper(),
        "timeframe": getattr(candles[-1].timeframe, "value", str(candles[-1].timeframe)),
        "candles": [
            {
                "open": _safe_float(candle.open),
                "high": _safe_float(candle.high),
                "low": _safe_float(candle.low),
                "close": _safe_float(candle.close),
                "volume": _safe_float(candle.volume),
                "start_time_ms": candle.start_time_ms,
                "end_time_ms": candle.end_time_ms,
            }
            for candle in candles
        ],
        "trend": trend,
        "latest_close": _safe_float(candles[-1].close),
        "range_high": _safe_float(range_high),
        "range_low": _safe_float(range_low),
        "volume_total": _safe_float(volume_total),
        "missing_data": [],
        "source": source,
        "live_trading_enabled": False,
        "public_data_only": True,
        "decision_rule": "Candle evidence is advisory; risk and zero-hallucination gates still decide.",
    }
    return ok(redact_sensitive(payload), "Candle detail loaded.")
