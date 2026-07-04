from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PersistentRecord:
    category: str
    payload: dict[str, Any]
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class BotRuntimeStateRecord:
    state: str
    shutdown_state: str
    healthy: bool
    failure_state: str = "NONE"
    open_paper_positions: int = 0
    interrupted_shutdown: bool = False
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class DailyPerformanceSummary:
    date: str
    paper_starting_balance: float
    ending_balance: float
    realized_pnl: float
    unrealized_pnl: float
    decisions: int
    skipped_trades: int
    risk_rejections: int
    hallucination_blocks: int
    paper_trades: int
    winning_trades: int
    losing_trades: int
    drawdown: float
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class SettingsRecord:
    key: str
    value: dict[str, Any]
    updated_at: str = field(default_factory=utc_now)
