from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trading_os.api.dependencies import get_backend, latest_audit_events, latest_decisions
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok, redact_sensitive
from trading_os.intelligence.candle_study import CandleStudy, CandleStudyEngine
from trading_os.market.candle_engine import Candle
from trading_os.market.live_public_data import BinancePublicMarketDataClient
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


def _latest_audit_payload(event_type: str, limit: int = 200) -> dict[str, Any] | None:
    for event in reversed(latest_audit_events(limit=limit)):
        if event.get("event_type") == event_type:
            payload = _payload(event)
            return {"created_at": event.get("created_at", ""), **payload}
    return None


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


@router.get("/paper-scan-summary")
def paper_scan_summary() -> dict[str, object]:
    backend = get_backend()
    auto_status = backend.paper_auto_trader.status()
    latest_tick = _latest_audit_payload("paper_auto_trader_tick")
    latest_scan = _latest_audit_payload("paper_auto_trader_scan")
    latest_pipeline = _latest_audit_payload("decision_to_trade_pipeline_result")
    latest_skip = _latest_audit_payload("skipped_trade")
    latest_fill = _latest_audit_payload("paper_order_fill")
    latest = latest_tick or auto_status.get("last_result") or {}
    payload = {
        "latest_symbol": latest.get("symbol", "unknown"),
        "latest_timeframe": latest.get("timeframe", "unknown"),
        "latest_action": latest.get("action", latest.get("status", "unknown")),
        "latest_status": latest.get("status", "unknown"),
        "latest_confidence": latest.get("confidence", 0.0),
        "latest_reason": latest.get("reason", "No paper scan result available."),
        "latest_timestamp": latest.get("timestamp", latest.get("created_at", "")),
        "trade_allowed": bool(latest.get("paper_fill_id")),
        "paper_fill_id": latest.get("paper_fill_id", ""),
        "why_not_traded": (
            latest.get("reason")
            or (latest_skip or {}).get("reason")
            or "No paper trade was opened by policy."
        ),
        "latest_scan_available": latest_scan is not None,
        "latest_pipeline_status": (latest_pipeline or {}).get("status", "unknown"),
        "latest_fill_available": latest_fill is not None,
        "run_count": auto_status.get("run_count", 0),
        "live_trading_enabled": False,
        "public_data_only": True,
    }
    return ok(redact_sensitive(payload), "Paper scan summary loaded.")


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


@router.get("/paper-demo-readiness")
def paper_demo_readiness() -> dict[str, object]:
    backend = get_backend()
    audit_events = latest_audit_events(limit=250)
    has_market_snapshot = any(
        event.get("event_type") == "market_snapshot" for event in audit_events
    )
    has_ai_decision = bool(latest_decisions(limit=1))
    has_evidence = any(event.get("event_type") in INTELLIGENCE_TYPES for event in audit_events)
    has_pipeline = any(
        event.get("event_type") == "decision_to_trade_pipeline_result" for event in audit_events
    )
    has_scan = any(event.get("event_type") == "paper_auto_trader_scan" for event in audit_events)
    has_candle_data = bool(
        backend.candle_engine.candles
        or [
            item
            for item in backend.repository.list_market_intelligence_snapshots(limit=20)
            if item.get("type") == "candle_archive"
        ]
    )
    checks = [
        {
            "name": "Paper mode default",
            "passed": backend.config.runtime_mode.value == "paper",
            "detail": "Trading mode must remain paper.",
        },
        {
            "name": "Live trading disabled",
            "passed": not backend.config.enable_live_trading,
            "detail": "No real Binance order placement is enabled.",
        },
        {
            "name": "Withdrawals unsupported",
            "passed": not backend.config.allow_withdraw_permissions,
            "detail": "Withdrawal permission is blocked.",
        },
        {
            "name": "Public market snapshot available",
            "passed": has_market_snapshot,
            "detail": "Paper scanner has read public market data.",
        },
        {
            "name": "Candle detail available",
            "passed": has_candle_data,
            "detail": "Candle memory or persisted archive exists.",
        },
        {
            "name": "Market evidence feed available",
            "passed": has_evidence,
            "detail": "Candle/order book/whale/news/structure evidence has been logged.",
        },
        {
            "name": "AI decision recorded",
            "passed": has_ai_decision,
            "detail": "Latest BUY/SELL/HOLD/SKIP decision is persisted/audited.",
        },
        {
            "name": "Pipeline result recorded",
            "passed": has_pipeline,
            "detail": "Decision-to-trade paper pipeline has completed.",
        },
        {
            "name": "Paper scanner run available",
            "passed": has_scan,
            "detail": "At least one safe public-data paper scan is available.",
        },
        {
            "name": "APK monitoring contract ready",
            "passed": True,
            "detail": "Status, charts, timelines, candle detail, and evidence routes exist.",
        },
    ]
    passed = len([item for item in checks if item["passed"]])
    monitoring_percent = int(round(passed / len(checks) * 100))
    demo_percent = monitoring_percent if has_scan and has_pipeline else min(monitoring_percent, 80)
    payload = {
        "paper_backend_apk_monitoring_percent": monitoring_percent,
        "paper_demo_readiness_percent": demo_percent,
        "ready_for_paper_demo": demo_percent == 100,
        "checks": checks,
        "remaining": [item for item in checks if not item["passed"]],
        "live_trading_enabled": False,
        "public_data_only": True,
        "real_money_ready": False,
    }
    return ok(redact_sensitive(payload), "Paper demo readiness loaded.")


def _safe_float(value: float) -> float:
    return round(float(value), 8)


def _study_payload(study: CandleStudy) -> dict[str, object]:
    return {
        "symbol": study.symbol,
        "timeframe": study.timeframe.value,
        "candle_count": study.candle_count,
        "latest_close": study.latest_close,
        "price_change_pct": study.price_change_pct,
        "trend": study.trend,
        "move_reason": study.move_reason,
        "evidence": study.evidence,
        "learning_notes": study.learning_notes,
        "confidence_score": study.confidence_score,
        "missing_data": study.missing_data,
    }


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


@router.get("/candle-study")
def candle_study(
    symbol: str = "BTCUSDT",
    timeframes: str = "5m,10m,1h,4h,8h,24h,1M",
    limit: int = 80,
) -> dict[str, object]:
    backend = get_backend()
    safe_limit = min(max(int(limit), 20), 200)
    requested = [item.strip() for item in timeframes.split(",") if item.strip()]
    if not requested:
        requested = ["5m", "10m", "1h", "4h", "8h", "24h", "1M"]
    client = BinancePublicMarketDataClient()
    study_engine = CandleStudyEngine()
    studies: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []

    for item in requested[:10]:
        try:
            tf = normalize_timeframe(item)
            bundle = client.fetch_bundle(
                symbol=symbol,
                timeframe=tf,
                candle_limit=safe_limit,
                order_book_limit=5,
                trade_limit=5,
            )
            backend.candle_engine.collect(bundle.candles)
            backend.repository.save_market_intelligence_snapshot(
                {
                    "type": "candle_archive",
                    "symbol": bundle.symbol,
                    "timeframe": bundle.timeframe.value,
                    "source": "binance_public_klines",
                    "public_data_only": True,
                    "live_trading_enabled": False,
                    "timestamp": bundle.evidence[0].timestamp,
                    "candles": [
                        {
                            "symbol": candle.symbol,
                            "timeframe": candle.timeframe.value,
                            "open": candle.open,
                            "high": candle.high,
                            "low": candle.low,
                            "close": candle.close,
                            "volume": candle.volume,
                            "start_time_ms": candle.start_time_ms,
                            "end_time_ms": candle.end_time_ms,
                        }
                        for candle in bundle.candles
                    ],
                }
            )
            study = study_engine.study(bundle.symbol, bundle.timeframe, bundle.candles)
            studies.append(_study_payload(study))
            backend.audit_logger.log(
                "candle_study",
                {
                    **_study_payload(study),
                    "public_data_only": True,
                    "live_trading_enabled": False,
                },
            )
        except Exception as exc:
            errors.append(
                {
                    "timeframe": item,
                    "error": exc.__class__.__name__,
                    "reason": "Candle study skipped safely for this timeframe.",
                }
            )

    payload = {
        "symbol": symbol.upper(),
        "studies": studies,
        "errors": errors,
        "self_learning_mode": "advisory_evidence_based",
        "learning_rule": "No Data = No Trade; candle learning cannot auto-change strategy or enable live trading.",
        "supported_timeframes": ["5m", "10m", "1h", "4h", "8h", "24h", "1M"],
        "live_trading_enabled": False,
        "public_data_only": True,
    }
    return ok(redact_sensitive(payload), "Multi-timeframe candle study loaded.")
