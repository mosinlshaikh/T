from __future__ import annotations

from typing import Any

from trading_os.analytics.safety_score import SafetyScoreEngine
from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.reports.generator import ReportGenerator
from trading_os.reports.statement import StatementEngine

router = APIRouter(prefix="/reports", tags=["reports"])


def _generator() -> ReportGenerator:
    backend = get_backend()
    safety = SafetyScoreEngine(
        repository=backend.repository,
        config=backend.config,
        vault=backend.api_vault,
        emergency_state=backend.runtime_supervisor.state.value,
    )
    return ReportGenerator(
        repository=backend.repository,
        portfolio=backend.portfolio,
        safety_score_engine=safety,
    )


@router.get("/daily")
def daily_report() -> dict[str, object]:
    return ok(_generator().daily_report(), "Daily paper report loaded.")


@router.get("/statement")
def statement_report(hours: int = 24) -> dict[str, object]:
    backend = get_backend()
    return ok(
        StatementEngine(backend.repository).build(hours=hours),
        "Paper profit/loss statement loaded.",
    )


@router.get("/statement-daily")
def daily_statement_report() -> dict[str, object]:
    backend = get_backend()
    return ok(
        StatementEngine(backend.repository).build(hours=24),
        "24-hour paper profit/loss statement loaded.",
    )


@router.get("/statement-7d")
def seven_day_statement_report() -> dict[str, object]:
    backend = get_backend()
    return ok(
        StatementEngine(backend.repository).build(hours=168),
        "7-day paper profit/loss statement loaded.",
    )


@router.get("/weekly")
def weekly_report() -> dict[str, object]:
    return ok(_generator().weekly_report(), "Weekly paper report loaded.")


@router.get("/monthly")
def monthly_report() -> dict[str, object]:
    return ok(_generator().monthly_report(), "Monthly paper report loaded.")


@router.get("/performance")
def performance_report() -> dict[str, object]:
    return ok(_generator().latest_performance_snapshot(), "Performance report loaded.")


@router.get("/risk")
def risk_report() -> dict[str, object]:
    return ok(_generator().risk_report(), "Risk report loaded.")


@router.get("/hallucination")
def hallucination_report() -> dict[str, object]:
    return ok(_generator().hallucination_safety_report(), "Hallucination safety report loaded.")


@router.get("/skipped-trades")
def skipped_trade_report() -> dict[str, object]:
    return ok(_generator().skipped_trade_report(), "Skipped trade report loaded.")


@router.get("/strategies")
def strategy_report() -> dict[str, object]:
    return ok(_generator().strategy_comparison_report(), "Strategy report loaded.")


@router.get("/runtime")
def runtime_report() -> dict[str, object]:
    return ok(_generator().shutdown_runtime_report(), "Runtime report loaded.")


@router.get("/dashboard-charts")
def dashboard_charts() -> dict[str, object]:
    backend = get_backend()
    decisions = backend.repository.list_ai_decisions(500)
    action_counts = {"BUY": 0, "SELL": 0, "HOLD": 0, "SKIP": 0}
    confidence_values: list[float] = []
    for decision in decisions:
        action = str(decision.get("action", "SKIP")).upper()
        action_counts[action if action in action_counts else "SKIP"] += 1
        confidence_values.append(float(decision.get("confidence", 0.0) or 0.0))
    confidence_profile = {
        "average": (
            round(sum(confidence_values) / len(confidence_values), 4) if confidence_values else 0.0
        ),
        "high": len([item for item in confidence_values if item >= 0.7]),
        "medium": len([item for item in confidence_values if 0.45 <= item < 0.7]),
        "low": len([item for item in confidence_values if item < 0.45]),
    }
    session = backend.paper_session_scheduler.status()
    return ok(
        {
            "action_counts": action_counts,
            "confidence_profile": confidence_profile,
            "paper_session": {
                "running": session["running"],
                "scan_count": session["scan_count"],
                "best_candidate": (
                    session.get("last_scan", {}).get("best_candidate")
                    if isinstance(session.get("last_scan"), dict)
                    else None
                ),
            },
            "live_trading_enabled": False,
            "public_data_only": True,
        },
        "Dashboard chart data loaded.",
    )


def _timeline_item(
    timestamp: str,
    event_type: str,
    title: str,
    detail: str,
    status: str = "paper",
    symbol: str = "",
) -> dict[str, str]:
    return {
        "timestamp": timestamp or "unknown",
        "event_type": event_type,
        "title": title,
        "detail": detail or "unknown / insufficient data",
        "status": status,
        "symbol": symbol,
    }


def _decision_timeline(decisions: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for decision in decisions[-25:]:
        action = str(decision.get("action", decision.get("final_decision", "SKIP"))).upper()
        symbol = str(decision.get("symbol", ""))
        confidence = decision.get("confidence", "0.00")
        reason = str(decision.get("reason", "No reason persisted."))
        timestamp = str(decision.get("timestamp", decision.get("created_at", "")))
        items.append(
            _timeline_item(
                timestamp=timestamp,
                event_type="ai_decision",
                title=f"{action} {symbol}".strip(),
                detail=f"confidence={confidence}; {reason}",
                status=action,
                symbol=symbol,
            )
        )
    return items


def _trade_timeline(journal: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for entry in journal[-25:]:
        symbol = str(entry.get("symbol", ""))
        status = str(entry.get("status", entry.get("event_type", "paper_trade_event")))
        side = str(entry.get("side", entry.get("action", "PAPER")))
        price = entry.get("price", entry.get("fill_price", "unknown"))
        pnl = entry.get("realized_pnl", entry.get("unrealized_pnl", "0.00"))
        timestamp = str(entry.get("timestamp", entry.get("created_at", "")))
        items.append(
            _timeline_item(
                timestamp=timestamp,
                event_type="paper_trade",
                title=f"{side} {symbol}".strip(),
                detail=f"status={status}; price={price}; pnl={pnl}",
                status=status,
                symbol=symbol,
            )
        )
    return items


def _audit_timeline(events: list[dict[str, Any]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for event in events[-25:]:
        payload = event.get("payload", event)
        if not isinstance(payload, dict):
            payload = {}
        event_type = str(event.get("event_type", payload.get("event_type", "audit_event")))
        timestamp = str(event.get("created_at", payload.get("timestamp", "")))
        detail = str(
            payload.get("reason")
            or payload.get("summary")
            or payload.get("status")
            or payload.get("message")
            or "audit event"
        )
        items.append(
            _timeline_item(
                timestamp=timestamp,
                event_type=event_type,
                title=event_type.replace("_", " ").title(),
                detail=detail,
                status=str(payload.get("status", event_type)),
                symbol=str(payload.get("symbol", "")),
            )
        )
    return items


@router.get("/timelines")
def dashboard_timelines() -> dict[str, object]:
    backend = get_backend()
    decisions = backend.repository.list_ai_decisions(100)
    journal = backend.repository.list_trade_journal(100)
    audit_events = backend.repository.list_audit_events(100)
    return ok(
        {
            "decision_timeline": _decision_timeline(decisions),
            "trade_timeline": _trade_timeline(journal),
            "audit_timeline": _audit_timeline(audit_events),
            "live_trading_enabled": False,
            "public_data_only": True,
            "source": "persisted_paper_backend",
        },
        "Dashboard timelines loaded.",
    )
