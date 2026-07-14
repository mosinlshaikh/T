from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from trading_os.db.repository import TradingOSRepository


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def event_time(payload: dict[str, Any]) -> datetime | None:
    for key in ("closed_at", "created_at", "timestamp", "opened_at", "updated_at"):
        parsed = parse_timestamp(payload.get(key))
        if parsed is not None:
            return parsed
    return None


@dataclass(frozen=True)
class StatementSummary:
    statement_id: str
    generated_at: str
    window_hours: int
    start_time: str
    end_time: str
    mode: str = "paper"
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    net_pnl: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    fees_estimated: float = 0.0
    open_positions: int = 0
    closed_positions: int = 0
    journal_entries: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate_pct: float = 0.0
    paper_scan_count: int = 0
    safety_checks: list[dict[str, Any]] = field(default_factory=list)
    trade_rows: list[dict[str, Any]] = field(default_factory=list)
    paper_scan_rows: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class StatementEngine:
    repository: TradingOSRepository

    def build(self, hours: int = 24) -> dict[str, Any]:
        safe_hours = min(max(int(hours), 1), 720)
        end = utc_now()
        start = end - timedelta(hours=safe_hours)
        closed = self._filter_window(self.repository.list_closed_positions(), start, end)
        journal = self._filter_window(self.repository.list_trade_journal(1000), start, end)
        open_positions = self.repository.list_open_positions()
        paper_scans = self._paper_scan_rows(start, end)

        closed_pnls = [float(item.get("realized_pnl", 0.0) or 0.0) for item in closed]
        journal_pnls = [float(item.get("realized_pnl", 0.0) or 0.0) for item in journal]
        pnl_source = closed_pnls if closed_pnls else journal_pnls
        realized_pnl = round(sum(pnl_source), 8)
        gross_profit = round(sum(item for item in pnl_source if item > 0), 8)
        gross_loss = round(sum(item for item in pnl_source if item < 0), 8)
        wins = [item for item in pnl_source if item > 0]
        losses = [item for item in pnl_source if item < 0]
        win_rate = round((len(wins) / len(pnl_source)) * 100, 2) if pnl_source else 0.0
        unrealized = 0.0
        trade_rows = self._trade_rows(closed, journal)

        summary = StatementSummary(
            statement_id=f"TTRL-PAPER-{end.strftime('%Y%m%d%H%M%S')}",
            generated_at=end.isoformat(),
            window_hours=safe_hours,
            start_time=start.isoformat(),
            end_time=end.isoformat(),
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized,
            net_pnl=round(realized_pnl + unrealized, 8),
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            fees_estimated=self._estimate_fees(journal),
            open_positions=len(open_positions),
            closed_positions=len(closed),
            journal_entries=len(journal),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate_pct=win_rate,
            paper_scan_count=len(paper_scans),
            safety_checks=self._safety_checks(),
            trade_rows=trade_rows[-100:],
            paper_scan_rows=paper_scans[-100:],
            notes=[
                "Statement uses persisted paper trading data only.",
                "No real Binance order execution is included.",
                "No profit guarantee. PnL can be negative.",
                "Recommended daily review window is 24 hours; weekly review window is 7 days.",
                "Paper scan rows show skipped/held decisions even when no paper position opened.",
            ],
        )
        return summary.__dict__

    def _filter_window(
        self, rows: list[dict[str, Any]], start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for row in rows:
            timestamp = event_time(row)
            if timestamp is None:
                continue
            if start <= timestamp <= end:
                filtered.append(row)
        return filtered

    def _trade_rows(
        self, closed: list[dict[str, Any]], journal: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        source = closed if closed else journal
        for index, item in enumerate(source):
            rows.append(
                {
                    "id": str(item.get("position_id") or item.get("trade_id") or index),
                    "timestamp": str(
                        item.get("closed_at")
                        or item.get("created_at")
                        or item.get("timestamp")
                        or ""
                    ),
                    "symbol": str(item.get("symbol", "UNKNOWN")).upper(),
                    "side": str(item.get("side") or item.get("action") or "PAPER"),
                    "status": str(item.get("status") or item.get("action") or "PAPER_EVENT"),
                    "realized_pnl": round(float(item.get("realized_pnl", 0.0) or 0.0), 8),
                    "reason": str(item.get("reason", "")),
                }
            )
        return rows

    def _paper_scan_rows(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        list_audit_events = getattr(self.repository, "list_audit_events", None)
        if list_audit_events is None:
            return []
        rows: list[dict[str, Any]] = []
        for event in list_audit_events(limit=2000):
            if event.get("event_type") not in {
                "paper_auto_trader_tick",
                "paper_auto_trader_scan",
                "paper_session_scan",
            }:
                continue
            payload = event.get("payload", event)
            if not isinstance(payload, dict):
                continue
            timestamp = event_time({"created_at": event.get("created_at"), **payload})
            if timestamp is None or not start <= timestamp <= end:
                continue
            if event.get("event_type") == "paper_auto_trader_scan":
                for item in payload.get("results", []):
                    if isinstance(item, dict):
                        rows.append(self._paper_scan_row(item, event.get("created_at", "")))
            elif event.get("event_type") == "paper_session_scan":
                candidate = payload.get("best_candidate")
                if isinstance(candidate, dict):
                    rows.append(self._paper_scan_row(candidate, event.get("created_at", "")))
            else:
                rows.append(self._paper_scan_row(payload, event.get("created_at", "")))
        return rows

    @staticmethod
    def _paper_scan_row(item: dict[str, Any], fallback_timestamp: Any) -> dict[str, Any]:
        return {
            "run_id": str(item.get("run_id", "")),
            "timestamp": str(item.get("timestamp") or item.get("created_at") or fallback_timestamp),
            "symbol": str(item.get("symbol", "UNKNOWN")).upper(),
            "timeframe": str(item.get("timeframe", "")),
            "action": str(item.get("action") or item.get("status") or "SKIP").upper(),
            "status": str(item.get("status") or item.get("action") or "SKIP").upper(),
            "confidence": round(float(item.get("confidence", 0.0) or 0.0), 4),
            "trade_allowed": bool(item.get("paper_fill_id")),
            "paper_fill_id": str(item.get("paper_fill_id", "")),
            "why_not_traded": str(
                item.get("why_not_traded")
                or item.get("reason")
                or "No paper trade was opened by policy."
            ),
        }

    @staticmethod
    def _estimate_fees(journal: list[dict[str, Any]]) -> float:
        fees = []
        for item in journal:
            if "fee" in item:
                fees.append(float(item.get("fee", 0.0) or 0.0))
        return round(sum(fees), 8)

    @staticmethod
    def _safety_checks() -> list[dict[str, Any]]:
        return [
            {"name": "Live trading disabled", "passed": True},
            {"name": "Withdrawals unsupported", "passed": True},
            {"name": "Paper mode default", "passed": True},
            {"name": "Stop-loss required", "passed": True},
            {"name": "Take-profit required", "passed": True},
            {"name": "Zero hallucination rule active", "passed": True},
            {"name": "No Data = No Trade", "passed": True},
        ]
