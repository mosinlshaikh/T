from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PerformanceCard:
    label: str
    value: str | float | int
    status: str = "unknown"


@dataclass(frozen=True)
class PnlChartPoint:
    timestamp: str
    realized_pnl: float
    unrealized_pnl: float = 0.0


@dataclass(frozen=True)
class StrategyScoreCard:
    strategy: str
    signals: int
    win_rate: float | str
    realized_pnl: float | str
    status: str = "unknown"


@dataclass(frozen=True)
class RiskSummaryCard:
    label: str
    count: int
    severity: str


@dataclass(frozen=True)
class TimelineEvent:
    timestamp: str
    event_type: str
    title: str
    detail: str = ""


@dataclass(frozen=True)
class SafetyScoreCard:
    score: int
    level: str
    reasons: list[str] = field(default_factory=list)
    recommended_action: str = ""


@dataclass(frozen=True)
class DashboardDataContract:
    performance_cards: list[PerformanceCard] = field(default_factory=list)
    pnl_chart_data: list[PnlChartPoint] = field(default_factory=list)
    strategy_score_cards: list[StrategyScoreCard] = field(default_factory=list)
    risk_summary_cards: list[RiskSummaryCard] = field(default_factory=list)
    decision_timeline: list[TimelineEvent] = field(default_factory=list)
    trade_timeline: list[TimelineEvent] = field(default_factory=list)
    audit_timeline: list[TimelineEvent] = field(default_factory=list)
    shutdown_timeline: list[TimelineEvent] = field(default_factory=list)
    safety_score: SafetyScoreCard | None = None
