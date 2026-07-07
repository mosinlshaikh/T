from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from trading_os.analytics.safety_score import SafetyScoreEngine
from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend
from trading_os.reports.generator import ReportGenerator


@dataclass(frozen=True)
class PaperReportExport:
    day: str
    report_path: str
    logbook_path: str
    decisions: int
    paper_trades: int
    skipped_trades: int
    realized_pnl: float
    drawdown: float


def build_report_generator(backend: TradingOSBackend) -> ReportGenerator:
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


def export_daily_paper_report(
    backend: TradingOSBackend | None = None,
    day: str | None = None,
    output_dir: str = "reports/paper/daily",
    logbook_path: str = "docs/PAPER_TRADING_LOGBOOK.md",
) -> PaperReportExport:
    active_backend = backend or TradingOSBackend(config=TradingOSConfig.from_env())
    target_day = day or date.today().isoformat()
    generator = build_report_generator(active_backend)
    report = generator.daily_report(target_day)
    performance = report.get("performance", {})
    if not isinstance(performance, dict):
        performance = {}

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{target_day}.md"
    report_path.write_text(daily_report_to_markdown(report), encoding="utf-8")

    update_logbook_summary(Path(logbook_path), target_day, performance)

    return PaperReportExport(
        day=target_day,
        report_path=str(report_path),
        logbook_path=logbook_path,
        decisions=int(performance.get("decisions", 0) or 0),
        paper_trades=int(performance.get("paper_trades", 0) or 0),
        skipped_trades=int(performance.get("skipped_trades", 0) or 0),
        realized_pnl=float(performance.get("realized_pnl", 0.0) or 0.0),
        drawdown=float(performance.get("drawdown", 0.0) or 0.0),
    )


def daily_report_to_markdown(report: dict[str, Any]) -> str:
    performance = report.get("performance", {})
    safety = report.get("safety_score", {})
    if not isinstance(performance, dict):
        performance = {}
    if not isinstance(safety, dict):
        safety = {}

    lines = [
        f"# Paper Trading Daily Report - {report.get('date', '')}",
        "",
        "Research-only paper trading report. Not financial advice.",
        "",
        "## Safety",
        "",
        "| Item | Value |",
        "| --- | --- |",
        "| Mode | paper |",
        "| Live trading | disabled |",
        "| Withdrawals | unsupported |",
        f"| Safety score | {safety.get('score', 'unknown')} / {enum_text(safety.get('level', 'UNKNOWN'))} |",
        "",
        "## Performance",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "paper_starting_balance",
        "ending_balance",
        "realized_pnl",
        "unrealized_pnl",
        "decisions",
        "skipped_trades",
        "risk_rejections",
        "hallucination_blocks",
        "paper_trades",
        "winning_trades",
        "losing_trades",
        "drawdown",
    ]:
        lines.append(f"| {key} | {performance.get(key, 0)} |")

    lines.extend(
        [
            "",
            "## Decision Reviews",
            "",
        ]
    )
    reviews = report.get("decision_reviews", [])
    if isinstance(reviews, list) and reviews:
        for review in reviews[:10]:
            if isinstance(review, dict):
                lines.append(
                    f"- {review.get('symbol', 'UNKNOWN')} {review.get('decision_type', '')}: "
                    f"{enum_text(review.get('result', ''))} - {review.get('reason', '')}"
                )
    else:
        lines.append("- No decision reviews available yet.")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Paper results are not real account results.",
            "- Missing data or conflicting signals should produce SKIP/HOLD.",
            "- No profit is guaranteed.",
            "",
        ]
    )
    return "\n".join(lines)


def enum_text(value: Any) -> str:
    text = str(value)
    return text.split(".")[-1] if "." in text else text


def update_logbook_summary(logbook: Path, day: str, performance: dict[str, Any]) -> None:
    if not logbook.exists():
        return
    line = (
        f"| {day} | {int(performance.get('decisions', 0) or 0)} | "
        f"{int(performance.get('paper_trades', 0) or 0)} | "
        f"{int(performance.get('skipped_trades', 0) or 0)} | "
        f"{performance.get('realized_pnl', 0.0)} | "
        f"{performance.get('drawdown', 0.0)}% | Auto-generated daily snapshot |"
    )
    text = logbook.read_text(encoding="utf-8")
    marker = "## Auto-Generated Daily Snapshots"
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n\n| Date | Decisions | Paper Trades | Skipped | Realized PnL | Drawdown | Notes |\n| --- | ---: | ---: | ---: | ---: | ---: | --- |\n"
    lines = text.splitlines()
    lines = [existing for existing in lines if not existing.startswith(f"| {day} |")]
    insert_at = len(lines)
    lines.insert(insert_at, line)
    logbook.write_text("\n".join(lines) + "\n", encoding="utf-8")
