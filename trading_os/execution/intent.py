from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from trading_os.ai.decision_types import DecisionAction, VerifiedDecision
from trading_os.trade.lifecycle import RiskInfo, TradeContext


class OrderIntentType(str, Enum):
    MARKET_BUY = "MARKET_BUY"
    MARKET_SELL = "MARKET_SELL"
    LIMIT_BUY = "LIMIT_BUY"
    LIMIT_SELL = "LIMIT_SELL"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    PARTIAL_EXIT = "PARTIAL_EXIT"


@dataclass(frozen=True)
class ExecutionIntent:
    symbol: str
    side: str
    quantity: float
    stop_loss: float
    take_profit: float
    reason: str
    evidence_ids: list[str]
    risk_approval_id: str
    intent_type: OrderIntentType
    price: float | None = None
    live_enabled: bool = False
    intent_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ExecutionIntentLayer:
    live_enabled: bool = False

    def from_verified_decision(
        self,
        decision: VerifiedDecision,
        trade_context: TradeContext,
        quantity: float,
        intent_type: OrderIntentType | None = None,
    ) -> ExecutionIntent | None:
        if self.live_enabled:
            raise RuntimeError("Live execution is disabled. Only order intents are supported.")
        if not decision.verified_decision:
            return None
        if decision.action == DecisionAction.HOLD or decision.action == DecisionAction.SKIP:
            return None
        if not trade_context.risk_info.approved:
            return None

        resolved_type = intent_type or self._default_intent_type(decision.action)
        return ExecutionIntent(
            symbol=decision.symbol.upper(),
            side=decision.action.value,
            quantity=quantity,
            price=trade_context.entry if resolved_type in self._limit_types() else None,
            stop_loss=trade_context.stop_loss,
            take_profit=trade_context.take_profit,
            reason=decision.reason,
            evidence_ids=trade_context.evidence_ids,
            risk_approval_id=trade_context.risk_info.risk_approval_id,
            intent_type=resolved_type,
            live_enabled=False,
        )

    def exit_intent(
        self,
        context: TradeContext,
        quantity: float,
        intent_type: OrderIntentType,
        reason: str,
    ) -> ExecutionIntent:
        if intent_type not in {
            OrderIntentType.MARKET_SELL,
            OrderIntentType.STOP_LOSS,
            OrderIntentType.TAKE_PROFIT,
            OrderIntentType.PARTIAL_EXIT,
        }:
            raise ValueError("Exit intent must be sell, stop-loss, take-profit, or partial exit.")
        return ExecutionIntent(
            symbol=context.symbol.upper(),
            side="SELL" if context.side.upper() == "BUY" else "BUY",
            quantity=quantity,
            price=None,
            stop_loss=context.stop_loss,
            take_profit=context.take_profit,
            reason=reason,
            evidence_ids=context.evidence_ids,
            risk_approval_id=context.risk_info.risk_approval_id,
            intent_type=intent_type,
            live_enabled=False,
        )

    @staticmethod
    def _default_intent_type(action: DecisionAction) -> OrderIntentType:
        if action == DecisionAction.BUY:
            return OrderIntentType.MARKET_BUY
        if action == DecisionAction.SELL:
            return OrderIntentType.MARKET_SELL
        raise ValueError(f"Unsupported execution action: {action.value}")

    @staticmethod
    def _limit_types() -> set[OrderIntentType]:
        return {OrderIntentType.LIMIT_BUY, OrderIntentType.LIMIT_SELL}


def risk_info_from_id(risk_approval_id: str, reason: str = "Risk approved.") -> RiskInfo:
    return RiskInfo(approved=True, risk_approval_id=risk_approval_id, reason=reason)
