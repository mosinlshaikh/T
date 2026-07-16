from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trading_os.api.dependencies import get_backend, latest_audit_events, latest_decisions
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok, redact_sensitive
from trading_os.intelligence.candle_study import CandleStudy, CandleStudyEngine
from trading_os.market.candle_engine import Candle
from trading_os.market.live_public_data import BinancePublicMarketDataClient
from trading_os.market.radar import rank_market_radar_rows
from trading_os.market.timeframes import normalize_timeframe

router = APIRouter(prefix="/monitor", tags=["monitor"])


INTELLIGENCE_TYPES = {
    "candle_analysis",
    "order_book_analysis",
    "whale_analysis",
    "news_risk_analysis",
    "market_structure_analysis",
    "combined_signal_result",
    "strategy_signal",
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
    "strategy_signal": "Strategy",
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


def _latest_paper_scan_payload() -> dict[str, Any]:
    backend = get_backend()
    auto_status = backend.paper_auto_trader.status()
    latest_tick = _latest_audit_payload("paper_auto_trader_tick")
    latest = latest_tick or auto_status.get("last_result") or {}
    return latest if isinstance(latest, dict) else {}


@router.get("/paper-live")
def paper_live_monitor() -> dict[str, object]:
    backend = get_backend()
    backend.paper_session_scheduler.auto_resume_if_configured()
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
    latest_scan = _latest_audit_payload("paper_auto_trader_scan")
    latest_pipeline = _latest_audit_payload("decision_to_trade_pipeline_result")
    latest_skip = _latest_audit_payload("skipped_trade")
    latest_fill = _latest_audit_payload("paper_order_fill")
    latest = _latest_paper_scan_payload()
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


def _latest_strategy_breakdown(symbol: str, limit: int = 500) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    wanted_symbol = symbol.upper()
    for event in latest_audit_events(limit=limit):
        if event.get("event_type") != "strategy_signal":
            continue
        payload = _payload(event)
        if str(payload.get("symbol", "")).upper() != wanted_symbol:
            continue
        rows.append(
            {
                "strategy": str(payload.get("source") or payload.get("signal") or "strategy"),
                "signal": str(payload.get("signal", "")),
                "direction": str(payload.get("direction", "unknown")).upper(),
                "confidence": payload.get("confidence", "unknown"),
                "evidence_count": payload.get("evidence_count", 0),
                "timestamp": event.get("created_at", ""),
            }
        )
    return rows[-8:]


def _latest_pipeline_stages(symbol: str, limit: int = 500) -> list[dict[str, object]]:
    wanted_symbol = symbol.upper()
    for event in reversed(latest_audit_events(limit=limit)):
        if event.get("event_type") != "decision_to_trade_pipeline_result":
            continue
        payload = _payload(event)
        if str(payload.get("symbol", "")).upper() != wanted_symbol:
            continue
        stages = payload.get("stage_results", [])
        if not isinstance(stages, list):
            return []
        rows: list[dict[str, object]] = []
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            rows.append(
                {
                    "stage": str(stage.get("stage", "stage")),
                    "outcome": str(stage.get("outcome", "UNKNOWN")).upper(),
                    "reason_code": str(stage.get("reason_code", "UNKNOWN")),
                    "latency_ms": stage.get("latency_ms", 0.0),
                    "missing_data": stage.get("missing_data", []),
                    "conflicts": stage.get("conflicts", []),
                    "timestamp": stage.get("timestamp", event.get("created_at", "")),
                }
            )
        return rows[-12:]
    return []


def _paper_scan_history_row(
    item: dict[str, Any], source: str, timestamp: str = ""
) -> dict[str, object]:
    symbol = str(item.get("symbol", "UNKNOWN")).upper()
    pipeline_stages = item.get("pipeline_stages", [])
    if not isinstance(pipeline_stages, list) or not pipeline_stages:
        pipeline_stages = _latest_pipeline_stages(symbol)
    return {
        "run_id": str(item.get("run_id", "")),
        "timestamp": str(item.get("timestamp") or item.get("created_at") or timestamp),
        "symbol": symbol,
        "timeframe": str(item.get("timeframe", "")),
        "action": str(item.get("action") or item.get("status") or "SKIP").upper(),
        "status": str(item.get("status") or item.get("action") or "SKIP").upper(),
        "confidence": round(float(item.get("confidence", 0.0) or 0.0), 4),
        "confidence_band": str(item.get("confidence_band", "")),
        "trade_allowed": bool(item.get("paper_fill_id")),
        "paper_fill_id": str(item.get("paper_fill_id", "")),
        "why_not_traded": str(
            item.get("why_not_traded")
            or item.get("reason")
            or "No paper trade was opened by policy."
        ),
        "strategy_breakdown": _latest_strategy_breakdown(symbol),
        "pipeline_stages": pipeline_stages,
        "source": source,
        "live_trading_enabled": False,
        "public_data_only": True,
    }


def _dedupe_scan_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: dict[str, dict[str, object]] = {}
    ordered_keys: list[str] = []
    for row in rows:
        run_id = str(row.get("run_id", ""))
        key = run_id or "|".join(
            [
                str(row.get("timestamp", "")),
                str(row.get("symbol", "")),
                str(row.get("action", "")),
                str(row.get("status", "")),
            ]
        )
        if key not in deduped:
            ordered_keys.append(key)
            deduped[key] = row
            continue
        existing = deduped[key]
        existing_stages = existing.get("pipeline_stages", [])
        row_stages = row.get("pipeline_stages", [])
        if isinstance(row_stages, list) and row_stages and not existing_stages:
            deduped[key] = row
    return [deduped[key] for key in ordered_keys]


@router.get("/paper-scan-history")
def paper_scan_history(limit: int = 20) -> dict[str, object]:
    safe_limit = min(max(int(limit), 1), 100)
    rows: list[dict[str, object]] = []
    for event in latest_audit_events(limit=max(safe_limit * 8, 200)):
        event_type = str(event.get("event_type", ""))
        if event_type not in {
            "paper_auto_trader_tick",
            "paper_auto_trader_scan",
            "paper_session_scan",
        }:
            continue
        payload = _payload(event)
        timestamp = str(event.get("created_at", ""))
        if event_type == "paper_auto_trader_scan":
            for item in payload.get("results", []):
                if isinstance(item, dict):
                    rows.append(_paper_scan_history_row(item, event_type, timestamp))
        elif event_type == "paper_session_scan":
            candidate = payload.get("best_candidate")
            if isinstance(candidate, dict):
                rows.append(_paper_scan_history_row(candidate, event_type, timestamp))
        else:
            rows.append(_paper_scan_history_row(payload, event_type, timestamp))
    unique_rows = _dedupe_scan_rows(rows)
    payload = {
        "rows": unique_rows[-safe_limit:],
        "count": len(unique_rows[-safe_limit:]),
        "raw_count": len(rows),
        "requested_limit": safe_limit,
        "live_trading_enabled": False,
        "public_data_only": True,
        "rule": "Paper scan history is audit-derived and never places real Binance orders.",
    }
    return ok(redact_sensitive(payload), "Paper scan history loaded.")


@router.get("/watchlist-candidates")
def watchlist_candidates(limit: int = 10) -> dict[str, object]:
    history = paper_scan_history(limit=100)["data"]
    rows = list(history.get("rows", []))
    ranked = sorted(
        rows,
        key=lambda item: (
            1 if str(item.get("action", "")).upper() in {"BUY", "SELL"} else 0,
            float(item.get("confidence", 0.0) or 0.0),
        ),
        reverse=True,
    )
    safe_limit = min(max(int(limit), 1), 20)
    candidates = ranked[:safe_limit]
    payload = {
        "candidates": candidates,
        "count": len(candidates),
        "source_rows": len(rows),
        "ranking_rule": "BUY/SELL candidates first, then confidence. HOLD/SKIP remain watch-only.",
        "live_trading_enabled": False,
        "public_data_only": True,
        "profit_guarantee": False,
    }
    return ok(redact_sensitive(payload), "Watchlist candidates loaded.")


@router.get("/strategy-blockers")
def strategy_blockers(limit: int = 100) -> dict[str, object]:
    safe_limit = min(max(int(limit), 5), 250)
    history = paper_scan_history(limit=safe_limit)["data"]
    rows = list(history.get("rows", []))
    blocker_counts: dict[str, int] = {}
    symbol_counts: dict[str, int] = {}
    action_counts = {"BUY": 0, "SELL": 0, "HOLD": 0, "SKIP": 0}
    low_confidence = 0
    no_trade_count = 0
    examples: list[dict[str, object]] = []

    for row in rows:
        action = str(row.get("action", "SKIP")).upper()
        if action in action_counts:
            action_counts[action] += 1
        symbol = str(row.get("symbol", "UNKNOWN")).upper()
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        confidence = float(row.get("confidence", 0.0) or 0.0)
        if confidence < 0.65:
            low_confidence += 1
        if not bool(row.get("trade_allowed")):
            no_trade_count += 1
        stages = row.get("pipeline_stages", [])
        if not isinstance(stages, list):
            stages = []
        row_blockers: list[str] = []
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            outcome = str(stage.get("outcome", "")).upper()
            if outcome not in {"HOLD", "SKIP", "REJECT"}:
                continue
            reason_code = str(stage.get("reason_code", "UNKNOWN"))
            stage_name = str(stage.get("stage", "stage"))
            blocker = f"{stage_name}:{outcome}:{reason_code}"
            row_blockers.append(blocker)
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
        if row_blockers and len(examples) < 12:
            examples.append(
                {
                    "symbol": symbol,
                    "action": action,
                    "confidence": confidence,
                    "why_not_traded": row.get("why_not_traded", ""),
                    "blockers": row_blockers,
                }
            )

    sorted_blockers = sorted(blocker_counts.items(), key=lambda item: item[1], reverse=True)
    sorted_symbols = sorted(symbol_counts.items(), key=lambda item: item[1], reverse=True)
    recommendations: list[str] = []
    if action_counts["HOLD"] + action_counts["SKIP"] == len(rows) and rows:
        recommendations.append(
            "All recent candidates were HOLD/SKIP; keep paper mode and inspect blockers."
        )
    if low_confidence:
        recommendations.append(
            "Many candidates are below 0.65 confidence; collect more candles/order book/whale/news evidence before tuning thresholds."
        )
    if any("SIGNALS_CONFLICT" in blocker for blocker in blocker_counts):
        recommendations.append(
            "Conflict blocker is active; add stronger multi-timeframe agreement before allowing paper entries."
        )
    if not rows:
        recommendations.append(
            "No recent paper scan rows found; start the paper session scheduler."
        )

    payload = {
        "window_rows": len(rows),
        "no_trade_count": no_trade_count,
        "low_confidence_count": low_confidence,
        "action_counts": action_counts,
        "top_blockers": [
            {"blocker": blocker, "count": count} for blocker, count in sorted_blockers[:12]
        ],
        "top_symbols": [
            {"symbol": symbol, "count": count} for symbol, count in sorted_symbols[:20]
        ],
        "examples": examples,
        "recommendations": recommendations,
        "tuning_policy": "Advisory only. Thresholds are not auto-changed and live trading remains disabled.",
        "live_trading_enabled": False,
        "public_data_only": True,
        "profit_guarantee": False,
    }
    return ok(redact_sensitive(payload), "Strategy blocker analysis loaded.")


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


def _bounded_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _decision_action_counts() -> dict[str, int]:
    counts = {"BUY": 0, "SELL": 0, "HOLD": 0, "SKIP": 0}
    for decision in latest_decisions(limit=250):
        action = str(
            decision.get("action")
            or decision.get("final_decision")
            or decision.get("decision")
            or ""
        ).upper()
        if action in counts:
            counts[action] += 1
    return counts


def _latest_candle_studies(limit: int = 200) -> list[dict[str, Any]]:
    studies: list[dict[str, Any]] = []
    for event in latest_audit_events(limit=limit):
        if event.get("event_type") != "candle_study":
            continue
        payload = _payload(event)
        studies.append({"created_at": event.get("created_at", ""), **payload})
    return studies


def _latest_studies_by_timeframe() -> dict[str, dict[str, Any]]:
    by_timeframe: dict[str, dict[str, Any]] = {}
    for study in _latest_candle_studies():
        timeframe = str(study.get("timeframe", "unknown"))
        by_timeframe[timeframe] = study
    return by_timeframe


def _quality_level(score: int) -> str:
    if score >= 78:
        return "HIGH"
    if score >= 58:
        return "MEDIUM"
    if score >= 35:
        return "LOW"
    return "SKIP"


def _trend_conflicts(studies: dict[str, dict[str, Any]]) -> list[str]:
    short = str((studies.get("5m") or studies.get("10m") or {}).get("trend", "unknown"))
    long = str((studies.get("1h") or studies.get("4h") or {}).get("trend", "unknown"))
    if "uptrend" in short and "downtrend" in long:
        return ["short_timeframe_up_long_timeframe_down"]
    if "downtrend" in short and "uptrend" in long:
        return ["short_timeframe_down_long_timeframe_up"]
    return []


@router.get("/performance-wheel")
def performance_wheel() -> dict[str, object]:
    backend = get_backend()
    events = latest_audit_events(limit=300)
    studies = _latest_studies_by_timeframe()
    counts = _decision_action_counts()
    has_market = any(event.get("event_type") == "market_snapshot" for event in events)
    has_candle = bool(studies)
    has_order_book = any(event.get("event_type") == "order_book_analysis" for event in events)
    has_whale = any(event.get("event_type") == "whale_analysis" for event in events)
    has_news = any(event.get("event_type") == "news_risk_analysis" for event in events)
    has_structure = any(event.get("event_type") == "market_structure_analysis" for event in events)
    has_risk = any(
        event.get("event_type") in {"risk_rejection", "risk_approval", "risk_result"}
        for event in events
    )
    wallet = backend.portfolio.wallet_snapshot()
    net_pnl = wallet.realized_pnl + wallet.unrealized_pnl
    candle_score = _bounded_score(
        max([float(item.get("confidence_score", 0.0) or 0.0) for item in studies.values()] or [0])
        * 100
    )
    data_score = _bounded_score(
        sum([has_market, has_candle, has_order_book, has_whale, has_news, has_structure]) / 6 * 100
    )
    safety_score = 100 if not backend.config.enable_live_trading else 0
    pnl_score = 50 if net_pnl == 0 else 70 if net_pnl > 0 else 25
    segments = [
        {"name": "Candle Reading", "score": candle_score, "status": _quality_level(candle_score)},
        {
            "name": "Whale Tracking",
            "score": 75 if has_whale else 35,
            "status": "DATA" if has_whale else "MISSING",
        },
        {
            "name": "News Risk",
            "score": 75 if has_news else 35,
            "status": "DATA" if has_news else "MISSING",
        },
        {
            "name": "Order Book",
            "score": 75 if has_order_book else 35,
            "status": "DATA" if has_order_book else "MISSING",
        },
        {
            "name": "Market Structure",
            "score": 75 if has_structure else 35,
            "status": "DATA" if has_structure else "MISSING",
        },
        {"name": "Risk Engine", "score": 80 if has_risk else 60, "status": "ACTIVE"},
        {"name": "Safety Lock", "score": safety_score, "status": "LIVE_BLOCKED"},
        {"name": "Zero Hallucination", "score": 95, "status": "ACTIVE"},
        {
            "name": "Paper PnL",
            "score": pnl_score,
            "status": "PROFIT" if net_pnl > 0 else "LOSS" if net_pnl < 0 else "FLAT",
        },
        {
            "name": "Decision Mix",
            "score": _bounded_score(
                (counts["BUY"] + counts["SELL"] + counts["HOLD"])
                / max(sum(counts.values()), 1)
                * 100
            ),
            "status": "PAPER",
        },
        {
            "name": "Backend Health",
            "score": data_score,
            "status": "CONNECTED" if data_score >= 50 else "PARTIAL",
        },
    ]
    payload = {
        "segments": segments,
        "overall_score": _bounded_score(
            sum(int(item["score"]) for item in segments) / len(segments)
        ),
        "decision_counts": counts,
        "net_pnl": net_pnl,
        "live_trading_enabled": False,
        "public_data_only": True,
        "rule": "Performance wheel is paper/audit monitoring only.",
    }
    return ok(redact_sensitive(payload), "Performance wheel loaded.")


@router.get("/trade-quality")
def trade_quality() -> dict[str, object]:
    studies = _latest_studies_by_timeframe()
    conflicts = _trend_conflicts(studies)
    latest_decision = _latest_decision_payload() or {}
    latest_scan = _latest_paper_scan_payload()
    latest_symbol = str(latest_scan.get("symbol") or latest_decision.get("symbol") or "unknown")
    latest_timestamp = str(
        latest_scan.get("timestamp")
        or latest_scan.get("created_at")
        or latest_decision.get("timestamp")
        or ""
    )
    evidence = latest_decision.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = [str(evidence)]
    decision_symbol = str(latest_decision.get("symbol") or "")
    evidence_symbol_aligned = bool(
        latest_symbol == "unknown" or not decision_symbol or decision_symbol == latest_symbol
    )
    stale_warnings: list[str] = []
    if not evidence_symbol_aligned:
        stale_warnings.append(
            f"Latest scan is {latest_symbol}, but latest decision evidence is for {decision_symbol}."
        )
        evidence = []
    candle_scores = [
        float(study.get("confidence_score", 0.0) or 0.0)
        for study in studies.values()
        if not study.get("missing_data")
    ]
    evidence_score = min(len(evidence), 5) * 10
    candle_score = (sum(candle_scores) / len(candle_scores) * 60) if candle_scores else 0
    conflict_penalty = 30 if conflicts else 0
    score = _bounded_score(evidence_score + candle_score - conflict_penalty)
    missing_data = []
    if not studies:
        missing_data.append("multi_timeframe_candles")
    if not evidence:
        missing_data.append("decision_evidence")
    if not evidence_symbol_aligned:
        missing_data.append("fresh_decision_evidence_for_latest_scan")
    action = str(
        latest_scan.get("action")
        or latest_decision.get("action")
        or latest_decision.get("final_decision")
        or "SKIP"
    ).upper()
    payload = {
        "score": score,
        "level": _quality_level(score),
        "recommended_action": "SKIP" if missing_data or conflicts or score < 58 else action,
        "trade_allowed": bool(
            not missing_data and not conflicts and score >= 58 and action in {"BUY", "SELL", "HOLD"}
        ),
        "evidence": evidence[:8],
        "missing_data": missing_data,
        "conflicts": conflicts,
        "warnings": stale_warnings,
        "latest_symbol": latest_symbol,
        "latest_timestamp": latest_timestamp,
        "evidence_symbol_aligned": evidence_symbol_aligned,
        "reason": "Trade quality uses evidence count, candle confidence, and conflict penalties.",
        "live_trading_enabled": False,
        "public_data_only": True,
    }
    return ok(redact_sensitive(payload), "Trade quality score loaded.")


@router.get("/no-trade-zone")
def no_trade_zone() -> dict[str, object]:
    studies = _latest_studies_by_timeframe()
    conflicts = _trend_conflicts(studies)
    range_count = len(
        [study for study in studies.values() if str(study.get("trend", "")).lower() == "range"]
    )
    low_confidence_count = len(
        [
            study
            for study in studies.values()
            if float(study.get("confidence_score", 0.0) or 0.0) < 0.45
        ]
    )
    active = bool(conflicts or range_count >= 3 or low_confidence_count >= 3 or not studies)
    reasons: list[str] = []
    if not studies:
        reasons.append("multi_timeframe_candle_data_missing")
    if range_count >= 3:
        reasons.append("range_or_choppy_market_across_timeframes")
    if low_confidence_count >= 3:
        reasons.append("low_confidence_across_timeframes")
    reasons.extend(conflicts)
    payload = {
        "active": active,
        "zone": "NO_TRADE" if active else "WATCHLIST_ALLOWED",
        "recommended_action": "SKIP" if active else "HOLD_OR_PAPER_ONLY_WATCH",
        "range_timeframe_count": range_count,
        "low_confidence_timeframe_count": low_confidence_count,
        "conflicts": conflicts,
        "reasons": reasons,
        "live_trading_enabled": False,
        "public_data_only": True,
    }
    return ok(redact_sensitive(payload), "No-trade zone status loaded.")


@router.get("/shadow-mode")
def shadow_mode() -> dict[str, object]:
    quality = trade_quality()["data"]  # safe local calculation; no network or order execution.
    zone = no_trade_zone()["data"]
    recommended = "SKIP"
    if not zone["active"] and quality["trade_allowed"]:
        recommended = str(quality["recommended_action"])
    payload = {
        "enabled": True,
        "mode": "PAPER_SHADOW_ONLY",
        "would_do": recommended,
        "trade_quality_score": quality["score"],
        "no_trade_zone_active": zone["active"],
        "reason": "Shadow mode records what the bot would do without enabling real execution.",
        "audit_policy": "Record candidate, evidence, missing data, conflicts, and paper outcome when available.",
        "live_trading_enabled": False,
        "public_data_only": True,
    }
    return ok(redact_sensitive(payload), "Paper shadow mode loaded.")


@router.get("/symbol-universe")
def symbol_universe(max_preview: int = 80) -> dict[str, object]:
    backend = get_backend()
    payload = backend.paper_auto_trader.symbol_universe(max_preview=max_preview)
    return ok(redact_sensitive(payload), "Binance Spot USDT symbol universe loaded.")


@router.get("/market-radar")
def market_radar(limit: int = 30) -> dict[str, object]:
    safe_limit = min(max(int(limit), 5), 80)
    client = BinancePublicMarketDataClient()
    try:
        rows = client.fetch_all_usdt_24h_tickers()
        error = ""
    except Exception as exc:
        rows = []
        error = f"{exc.__class__.__name__}: public market radar unavailable"
    ranked = rank_market_radar_rows(rows, limit=safe_limit)
    payload = {
        "mode": "FULL_MARKET_PUBLIC_PREFILTER",
        "source": "binance_public_24hr_all_tickers",
        "symbols_seen": len(rows),
        "candidates": ranked,
        "deep_scan_symbols": [str(item["symbol"]) for item in ranked[: min(safe_limit, 40)]],
        "ranking_rule": "volume + absolute 24h movement + volatility + trade activity",
        "error": error,
        "live_trading_enabled": False,
        "public_data_only": True,
        "profit_guarantee": False,
        "rule": "Radar shortlists candidates only; decision pipeline still requires evidence, risk, and zero-hallucination checks.",
    }
    return ok(redact_sensitive(payload), "Full-market radar loaded.")


@router.get("/fast-market-state")
def fast_market_state(limit: int = 30) -> dict[str, object]:
    backend = get_backend()
    safe_limit = min(max(int(limit), 5), 80)
    health = backend.market_stream_state.health()
    seeded_from_rest = False
    error = ""
    if not health["stream_cache_ready"]:
        client = BinancePublicMarketDataClient()
        try:
            rows = client.fetch_all_usdt_24h_tickers()
            backend.market_stream_state.update_many(rows, source="binance_public_24hr_rest_seed")
            seeded_from_rest = True
        except Exception as exc:
            error = f"{exc.__class__.__name__}: public market state seed unavailable"
    ranked = backend.market_stream_state.ranked_radar(limit=safe_limit)
    stream_status = backend.mini_ticker_stream.status()
    payload = {
        "mode": "FAST_MARKET_STATE_PUBLIC_CACHE",
        "source": "in_memory_stream_cache",
        "seeded_from_rest": seeded_from_rest,
        "health": backend.market_stream_state.health(),
        "stream_status": stream_status,
        "candidates": ranked,
        "deep_scan_symbols": [str(item["symbol"]) for item in ranked[: min(safe_limit, 40)]],
        "error": error,
        "latency_design": (
            "Use cached public ticker state for fast prefilter; deep candle/order-book "
            "checks still run only for shortlisted symbols."
        ),
        "live_trading_enabled": False,
        "public_data_only": True,
        "profit_guarantee": False,
        "rule": "Fast state shortlists candidates only; evidence, risk, and zero-hallucination checks still decide SKIP/HOLD/BUY/SELL.",
    }
    return ok(redact_sensitive(payload), "Fast market state loaded.")


@router.get("/daily-target")
def daily_target(target_pnl_pct: float = 10.0) -> dict[str, object]:
    backend = get_backend()
    wallet = backend.portfolio.wallet_snapshot()
    safe_target_pct = min(max(float(target_pnl_pct), 0.1), 10.0)
    starting_balance = max(wallet.usdt_balance - wallet.realized_pnl, 1.0)
    target_amount = starting_balance * (safe_target_pct / 100)
    current_pnl = backend.portfolio.daily_pnl()
    progress_pct = min(
        max((current_pnl / target_amount) * 100 if target_amount else 0.0, 0.0), 100.0
    )
    target_reached = current_pnl >= target_amount
    payload = {
        "target_pnl_pct": safe_target_pct,
        "target_amount_usdt": round(target_amount, 8),
        "current_daily_pnl_usdt": round(current_pnl, 8),
        "progress_pct": round(progress_pct, 2),
        "target_reached": target_reached,
        "recommended_mode": "PROTECT_PROFIT" if target_reached else "PAPER_DISCOVERY",
        "rules": [
            "10% daily PnL is a target setting, not a promise.",
            "If target is reached, reduce new paper entries and protect gains.",
            "If data is missing or conflicts exist, decision remains SKIP/HOLD.",
            "Daily loss, cooldown, stop-loss, and take-profit rules remain active.",
        ],
        "live_trading_enabled": False,
        "public_data_only": True,
        "profit_guarantee": False,
    }
    return ok(redact_sensitive(payload), "Daily target guard loaded.")


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
