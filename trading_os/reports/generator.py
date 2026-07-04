from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from trading_os.analytics.decision_review import DecisionReviewEngine
from trading_os.analytics.safety_score import SafetyScoreEngine
from trading_os.analytics.strategy_performance import StrategyPerformanceAnalyzer
from trading_os.db.performance import generate_daily_performance_summary
from trading_os.db.repository import TradingOSRepository
from trading_os.learning.feedback_engine import LearningFeedbackEngine
from trading_os.portfolio.state import PortfolioStateManager


@dataclass
class ReportGenerator:
    repository: TradingOSRepository
    portfolio: PortfolioStateManager
    safety_score_engine: SafetyScoreEngine

    def daily_report(self, day: str | None = None) -> dict[str, Any]:
        summary = generate_daily_performance_summary(self.repository, self.portfolio, day)
        return {
            "report_type": "daily",
            "date": day or date.today().isoformat(),
            "performance": asdict(summary),
            "strategy_performance": asdict(StrategyPerformanceAnalyzer(self.repository).analyze()),
            "decision_reviews": [
                asdict(item) for item in DecisionReviewEngine(self.repository).review_latest(10)
            ],
            "learning_feedback": asdict(LearningFeedbackEngine(self.repository).generate()),
            "safety_score": asdict(self.safety_score_engine.calculate()),
            "basis": "persisted paper data only",
        }

    def weekly_report(self) -> dict[str, Any]:
        return {"report_type": "weekly", "status": "skeleton", "basis": "persisted paper data only"}

    def monthly_report(self) -> dict[str, Any]:
        return {
            "report_type": "monthly",
            "status": "skeleton",
            "basis": "persisted paper data only",
        }

    def latest_performance_snapshot(self) -> dict[str, Any]:
        return asdict(StrategyPerformanceAnalyzer(self.repository).analyze())

    def risk_report(self) -> dict[str, Any]:
        audit = self.repository.list_audit_events(500)
        return {
            "risk_rejections": [
                item for item in audit if item.get("event_type") == "risk_rejection"
            ],
            "risk_results": self.repository.list_risk_results(100),
            "basis": "persisted risk events only",
        }

    def hallucination_safety_report(self) -> dict[str, Any]:
        audit = self.repository.list_audit_events(500)
        return {
            "blocked_hallucinations": [
                item for item in audit if item.get("event_type") == "blocked_hallucination"
            ],
            "verification_results": self.repository.list_zero_hallucination_results(100),
            "basis": "persisted verification events only",
        }

    def skipped_trade_report(self) -> dict[str, Any]:
        audit = self.repository.list_audit_events(500)
        return {
            "skipped_trades": [item for item in audit if item.get("event_type") == "skipped_trade"],
            "basis": "persisted skip events only",
        }

    def strategy_comparison_report(self) -> dict[str, Any]:
        return self.latest_performance_snapshot()

    def shutdown_runtime_report(self) -> dict[str, Any]:
        bot_state = self.repository.get_latest_bot_state()
        audit = self.repository.list_audit_events(500)
        return {
            "latest_bot_state": bot_state or {"status": "unknown"},
            "runtime_events": [
                item
                for item in audit
                if item.get("event_type")
                in {"runtime_heartbeat", "supervisor_state_change", "reconnect_attempt"}
            ],
            "basis": "persisted runtime events only",
        }

    @staticmethod
    def to_markdown(report: dict[str, Any]) -> str:
        lines = [f"# {str(report.get('report_type', 'report')).title()} Report", ""]
        for key, value in report.items():
            lines.append(f"## {key}")
            lines.append("```text")
            lines.append(str(value))
            lines.append("```")
        return "\n".join(lines)
