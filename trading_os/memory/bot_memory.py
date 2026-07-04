from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_os.db.repository import TradingOSRepository


@dataclass(frozen=True)
class BotMemorySnapshot:
    last_decisions: list[dict[str, Any]]
    recent_skipped_trades: list[dict[str, Any]]
    recent_risk_rejections: list[dict[str, Any]]
    recent_hallucination_blocks: list[dict[str, Any]]
    recent_winning_paper_trades: list[dict[str, Any]]
    recent_losing_paper_trades: list[dict[str, Any]]
    daily_pnl_memory: dict[str, Any]
    market_condition_history_summary: str
    strategy_performance_memory: dict[str, Any]
    missing_data: list[str] = field(default_factory=list)


@dataclass
class BotMemory:
    repository: TradingOSRepository

    def snapshot(self) -> BotMemorySnapshot:
        decisions = self.repository.list_ai_decisions(limit=20)
        audit_events = self.repository.list_audit_events(limit=200)
        journal = self.repository.list_trade_journal(limit=100)
        skipped = [item for item in audit_events if item.get("event_type") == "skipped_trade"]
        risks = [item for item in audit_events if item.get("event_type") == "risk_rejection"]
        hallucinations = [
            item for item in audit_events if item.get("event_type") == "blocked_hallucination"
        ]
        winners = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) > 0]
        losers = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) < 0]
        missing: list[str] = []
        if not decisions:
            missing.append("ai_decisions")
        if not journal:
            missing.append("trade_journal")

        return BotMemorySnapshot(
            last_decisions=decisions[-10:],
            recent_skipped_trades=skipped[-10:],
            recent_risk_rejections=risks[-10:],
            recent_hallucination_blocks=hallucinations[-10:],
            recent_winning_paper_trades=winners[-10:],
            recent_losing_paper_trades=losers[-10:],
            daily_pnl_memory=self._latest_daily_performance(),
            market_condition_history_summary=self._market_summary(audit_events),
            strategy_performance_memory=self._strategy_memory(audit_events),
            missing_data=missing,
        )

    def _latest_daily_performance(self) -> dict[str, Any]:
        records = self.repository.storage.list_records("daily_performance", 1, newest_first=True)
        return records[0]["payload"] if records else {"status": "unknown", "reason": "missing"}

    @staticmethod
    def _market_summary(audit_events: list[dict[str, Any]]) -> str:
        intelligence = [
            item
            for item in audit_events
            if str(item.get("event_type", "")).endswith("analysis")
            or item.get("event_type") == "combined_signal_result"
        ]
        if not intelligence:
            return "unknown: no persisted market intelligence evidence available."
        return f"evidence_available: {len(intelligence)} persisted intelligence events."

    @staticmethod
    def _strategy_memory(audit_events: list[dict[str, Any]]) -> dict[str, Any]:
        signals = [item for item in audit_events if item.get("event_type") == "strategy_signal"]
        if not signals:
            return {"status": "unknown", "reason": "missing strategy signal history"}
        return {"strategy_signal_events": len(signals)}
