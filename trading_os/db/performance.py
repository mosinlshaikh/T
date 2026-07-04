from __future__ import annotations

from dataclasses import asdict
from datetime import date

from trading_os.db.models import DailyPerformanceSummary
from trading_os.db.repository import TradingOSRepository
from trading_os.portfolio.state import PortfolioStateManager


def generate_daily_performance_summary(
    repository: TradingOSRepository,
    portfolio: PortfolioStateManager,
    day: str | None = None,
) -> DailyPerformanceSummary:
    target_day = day or date.today().isoformat()
    decisions = repository.list_ai_decisions(limit=500)
    audit_events = repository.list_audit_events(limit=1000)
    journal = repository.list_trade_journal(limit=500)
    wallet = portfolio.wallet_snapshot()
    wins = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) > 0]
    losses = [item for item in journal if float(item.get("realized_pnl", 0.0) or 0.0) < 0]
    return DailyPerformanceSummary(
        date=target_day,
        paper_starting_balance=portfolio.starting_balance,
        ending_balance=wallet.usdt_balance,
        realized_pnl=wallet.realized_pnl,
        unrealized_pnl=wallet.unrealized_pnl,
        decisions=len(decisions),
        skipped_trades=len(
            [item for item in audit_events if item.get("event_type") == "skipped_trade"]
        ),
        risk_rejections=len(
            [item for item in audit_events if item.get("event_type") == "risk_rejection"]
        ),
        hallucination_blocks=len(
            [item for item in audit_events if item.get("event_type") == "blocked_hallucination"]
        ),
        paper_trades=len(journal),
        winning_trades=len(wins),
        losing_trades=len(losses),
        drawdown=portfolio.drawdown_pct(),
    )


def save_daily_performance_summary(
    repository: TradingOSRepository,
    portfolio: PortfolioStateManager,
    day: str | None = None,
) -> dict[str, object]:
    summary = generate_daily_performance_summary(repository, portfolio, day)
    repository.save_daily_performance(summary)
    return asdict(summary)
