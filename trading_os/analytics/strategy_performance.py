from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_os.db.repository import TradingOSRepository


@dataclass(frozen=True)
class StrategyPerformanceReport:
    status: str
    total_signals_per_strategy: dict[str, int] = field(default_factory=dict)
    action_counts: dict[str, int] = field(default_factory=dict)
    paper_trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    win_rate: float | str = "unknown"
    realized_pnl: float | str = "unknown"
    unrealized_pnl: float | str = "unknown"
    average_pnl: float | str = "unknown"
    max_drawdown: float | str = "unknown"
    risk_rejection_count: int = 0
    hallucination_block_count: int = 0
    confidence_vs_outcome_summary: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class StrategyPerformanceAnalyzer:
    repository: TradingOSRepository

    def analyze(self) -> StrategyPerformanceReport:
        signals = self.repository.list_strategy_signals()
        journal = self.repository.list_trade_journal()
        audit = self.repository.list_audit_events(1000)
        decisions = self.repository.list_ai_decisions(500)
        snapshots = self.repository.storage.list_records("portfolio_snapshot", 500)
        if not signals and not journal and not decisions:
            return StrategyPerformanceReport(
                status="insufficient_data",
                reason="No persisted strategy, decision, or paper trade data available.",
            )

        total_by_strategy: dict[str, int] = {}
        action_counts = {"BUY": 0, "SELL": 0, "HOLD": 0, "SKIP": 0}
        for signal in signals:
            name = str(signal.get("signal") or signal.get("name") or "unknown_strategy")
            total_by_strategy[name] = total_by_strategy.get(name, 0) + 1
        for decision in decisions:
            action = str(decision.get("action", "SKIP")).upper()
            if action in action_counts:
                action_counts[action] += 1

        pnl_values = [float(item.get("realized_pnl", 0.0) or 0.0) for item in journal]
        wins = [value for value in pnl_values if value > 0]
        losses = [value for value in pnl_values if value < 0]
        paper_trade_count = len(journal)
        realized_pnl = round(sum(pnl_values), 8) if journal else "unknown"
        average_pnl = round(sum(pnl_values) / len(pnl_values), 8) if pnl_values else "unknown"
        win_rate: float | str = (
            round(len(wins) / paper_trade_count * 100, 4) if paper_trade_count else "unknown"
        )
        latest_snapshot = snapshots[-1]["payload"] if snapshots else {}
        unrealized_pnl = latest_snapshot.get("unrealized_pnl", "unknown")
        max_drawdown = self._max_drawdown()

        return StrategyPerformanceReport(
            status="ok",
            total_signals_per_strategy=total_by_strategy,
            action_counts=action_counts,
            paper_trade_count=paper_trade_count,
            win_count=len(wins),
            loss_count=len(losses),
            win_rate=win_rate,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            average_pnl=average_pnl,
            max_drawdown=max_drawdown,
            risk_rejection_count=len(
                [item for item in audit if item.get("event_type") == "risk_rejection"]
            ),
            hallucination_block_count=len(
                [item for item in audit if item.get("event_type") == "blocked_hallucination"]
            ),
            confidence_vs_outcome_summary=self._confidence_summary(decisions, pnl_values),
            reason="Report uses persisted paper data only.",
        )

    def _max_drawdown(self) -> float | str:
        summaries = self.repository.list_daily_performance(90)
        drawdowns = [float(item.get("drawdown", 0.0) or 0.0) for item in summaries]
        return round(max(drawdowns), 4) if drawdowns else "unknown"

    @staticmethod
    def _confidence_summary(
        decisions: list[dict[str, Any]], pnl_values: list[float]
    ) -> dict[str, Any]:
        if not decisions or not pnl_values:
            return {"status": "unknown", "reason": "decision/outcome link unavailable"}
        confidence_values = [float(item.get("confidence", 0.0) or 0.0) for item in decisions]
        return {
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 4),
            "outcome_records": len(pnl_values),
            "status": "aggregate_only",
            "reason": "Phase 8 has aggregate confidence and outcome data, not a guaranteed one-to-one link.",
        }
