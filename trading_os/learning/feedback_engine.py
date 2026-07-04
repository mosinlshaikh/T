from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_os.db.repository import TradingOSRepository


@dataclass(frozen=True)
class LearningFeedback:
    status: str
    signals_worked: list[str] = field(default_factory=list)
    signals_failed: list[str] = field(default_factory=list)
    signals_blocked: list[str] = field(default_factory=list)
    strategies_need_more_data: list[str] = field(default_factory=list)
    confidence_ranges: dict[str, Any] = field(default_factory=dict)
    skip_conditions: dict[str, Any] = field(default_factory=dict)
    risk_rules_saved_capital: list[str] = field(default_factory=list)
    advisory_only: bool = True
    reason: str = ""


@dataclass
class LearningFeedbackEngine:
    repository: TradingOSRepository

    def generate(self) -> LearningFeedback:
        decisions = self.repository.list_ai_decisions(500)
        signals = self.repository.list_strategy_signals(500)
        audit = self.repository.list_audit_events(1000)
        journal = self.repository.list_trade_journal(500)
        if not decisions and not signals and not journal:
            return LearningFeedback(
                status="insufficient_data",
                strategies_need_more_data=["all"],
                reason="No persisted paper-mode history is available.",
            )

        positive = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) > 0]
        negative = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) < 0]
        blocked = [
            str(item.get("payload", {}).get("symbol", "unknown"))
            for item in audit
            if item.get("event_type") in {"risk_rejection", "blocked_hallucination"}
        ]
        strategy_names = {
            str(item.get("signal") or item.get("name") or "unknown") for item in signals
        }
        confidence_values = [float(item.get("confidence", 0.0) or 0.0) for item in decisions]
        skipped = [item for item in audit if item.get("event_type") == "skipped_trade"]

        return LearningFeedback(
            status="ok",
            signals_worked=[item.get("symbol", "paper_trade") for item in positive],
            signals_failed=[item.get("symbol", "paper_trade") for item in negative],
            signals_blocked=blocked[-20:],
            strategies_need_more_data=(
                sorted(strategy_names) if not positive and not negative else []
            ),
            confidence_ranges=self._confidence_ranges(confidence_values),
            skip_conditions={
                "skipped_trade_count": len(skipped),
                "summary": "Persisted skip reasons only; no market facts invented.",
            },
            risk_rules_saved_capital=[
                str(item.get("payload", {}).get("reason", "risk_rejection"))
                for item in audit
                if item.get("event_type") == "risk_rejection"
            ],
            reason="Advisory feedback only. No strategy rules are changed.",
        )

    @staticmethod
    def _confidence_ranges(values: list[float]) -> dict[str, Any]:
        if not values:
            return {"status": "unknown", "reason": "missing confidence history"}
        return {
            "low_lt_0_4": len([item for item in values if item < 0.4]),
            "mid_0_4_to_0_7": len([item for item in values if 0.4 <= item < 0.7]),
            "high_gte_0_7": len([item for item in values if item >= 0.7]),
            "average": round(sum(values) / len(values), 4),
        }
