from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from trading_os.ai.decision_types import EvidenceItem
from trading_os.market.timeframes import Timeframe


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TradeState(str, Enum):
    NEW_SIGNAL = "NEW_SIGNAL"
    RISK_CHECK_PENDING = "RISK_CHECK_PENDING"
    APPROVED_FOR_PAPER = "APPROVED_FOR_PAPER"
    PAPER_OPEN = "PAPER_OPEN"
    PAPER_PARTIAL_EXIT = "PAPER_PARTIAL_EXIT"
    PAPER_CLOSED = "PAPER_CLOSED"
    LIVE_BLOCKED = "LIVE_BLOCKED"
    REJECTED_BY_RISK = "REJECTED_BY_RISK"
    REJECTED_BY_ZERO_HALLUCINATION = "REJECTED_BY_ZERO_HALLUCINATION"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class RiskInfo:
    approved: bool
    risk_approval_id: str = ""
    reason: str = ""
    max_risk_pct: float = 0.0
    rejections: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TradeContext:
    symbol: str
    timeframe: Timeframe
    side: str
    entry: float
    stop_loss: float
    take_profit: float
    confidence: float
    evidence: list[EvidenceItem]
    risk_info: RiskInfo
    state: TradeState = TradeState.NEW_SIGNAL
    trade_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @property
    def evidence_ids(self) -> list[str]:
        return [
            str(item.payload.get("evidence_id", f"{item.source}:{item.evidence_type.value}"))
            for item in self.evidence
        ]


@dataclass
class TradeLifecycleEngine:
    transitions: dict[TradeState, set[TradeState]] = field(
        default_factory=lambda: {
            TradeState.NEW_SIGNAL: {
                TradeState.RISK_CHECK_PENDING,
                TradeState.REJECTED_BY_ZERO_HALLUCINATION,
                TradeState.CANCELLED,
            },
            TradeState.RISK_CHECK_PENDING: {
                TradeState.APPROVED_FOR_PAPER,
                TradeState.REJECTED_BY_RISK,
                TradeState.LIVE_BLOCKED,
                TradeState.CANCELLED,
            },
            TradeState.APPROVED_FOR_PAPER: {
                TradeState.PAPER_OPEN,
                TradeState.CANCELLED,
                TradeState.LIVE_BLOCKED,
            },
            TradeState.PAPER_OPEN: {
                TradeState.PAPER_PARTIAL_EXIT,
                TradeState.PAPER_CLOSED,
                TradeState.CANCELLED,
            },
            TradeState.PAPER_PARTIAL_EXIT: {
                TradeState.PAPER_PARTIAL_EXIT,
                TradeState.PAPER_CLOSED,
                TradeState.CANCELLED,
            },
            TradeState.PAPER_CLOSED: set(),
            TradeState.LIVE_BLOCKED: set(),
            TradeState.REJECTED_BY_RISK: set(),
            TradeState.REJECTED_BY_ZERO_HALLUCINATION: set(),
            TradeState.CANCELLED: set(),
        }
    )

    def can_transition(self, current: TradeState, target: TradeState) -> bool:
        return target in self.transitions.get(current, set())

    def transition(
        self,
        context: TradeContext,
        target: TradeState,
        *,
        live_enabled: bool = False,
    ) -> TradeContext:
        if target == TradeState.LIVE_BLOCKED:
            return replace(context, state=target, updated_at=utc_now())
        if live_enabled:
            return replace(context, state=TradeState.LIVE_BLOCKED, updated_at=utc_now())
        if not self.can_transition(context.state, target):
            raise ValueError(f"Invalid trade transition: {context.state.value} -> {target.value}")
        return replace(context, state=target, updated_at=utc_now())
