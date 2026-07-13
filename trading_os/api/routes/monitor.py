from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trading_os.api.dependencies import get_backend, latest_audit_events, latest_decisions
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok, redact_sensitive

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
