from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_types import EvidenceItem, EvidenceType
from trading_os.security.kill_switch import EmergencyKillSwitch


@dataclass(frozen=True)
class RiskContext:
    symbol: str
    account_balance: float
    requested_trade_size: float
    current_exposure: float
    daily_realized_loss: float = 0.0
    consecutive_losses: int = 0
    minutes_since_last_loss: int | None = None
    stop_loss_present: bool = False
    take_profit_present: bool = False


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str
    rejections: list[str] = field(default_factory=list)


@dataclass
class RiskEngine:
    reserve_capital_pct: float = 10.0
    max_risk_exposure_pct: float = 5.0
    max_trade_size: float = 500.0
    daily_loss_limit_pct: float = 3.0
    consecutive_loss_limit: int = 3
    cooldown_after_loss_minutes: int = 30

    def evaluate(
        self, context: RiskContext, kill_switch: EmergencyKillSwitch | None = None
    ) -> RiskDecision:
        rejections: list[str] = []

        if kill_switch and kill_switch.active:
            rejections.append("Emergency kill switch is active.")
        if context.account_balance <= 0:
            rejections.append("Account balance must be positive.")
        if context.requested_trade_size <= 0:
            rejections.append("Requested trade size must be positive.")
        if context.requested_trade_size > self.max_trade_size:
            rejections.append("Requested trade size exceeds max trade size.")
        if context.requested_trade_size > self.available_capital_after_reserve(
            context.account_balance
        ):
            rejections.append("Requested trade size violates reserve capital lock.")
        if self.exposure_pct(context) > self.max_risk_exposure_pct:
            rejections.append("Exposure exceeds max risk exposure rule.")
        if self.daily_loss_pct(context) > self.daily_loss_limit_pct:
            rejections.append("Daily loss limit reached.")
        if context.consecutive_losses >= self.consecutive_loss_limit:
            rejections.append("Consecutive loss limit reached.")
        if self._cooldown_active(context):
            rejections.append("Cooldown after loss is active.")
        if not context.stop_loss_present:
            rejections.append("Stop-loss is required.")
        if not context.take_profit_present:
            rejections.append("Take-profit is required.")

        if rejections:
            return RiskDecision(False, "Risk rejected.", rejections)
        return RiskDecision(True, "Risk check passed.", [])

    def available_capital_after_reserve(self, balance: float) -> float:
        reserve = balance * (self.reserve_capital_pct / 100)
        return max(balance - reserve, 0.0)

    def exposure_pct(self, context: RiskContext) -> float:
        if context.account_balance <= 0:
            return 100.0
        return (
            (context.current_exposure + context.requested_trade_size) / context.account_balance
        ) * 100

    def daily_loss_pct(self, context: RiskContext) -> float:
        if context.account_balance <= 0:
            return 100.0
        return abs(min(context.daily_realized_loss, 0.0)) / context.account_balance * 100

    def to_evidence(self, decision: RiskDecision) -> EvidenceItem:
        return EvidenceItem(
            evidence_type=EvidenceType.RISK_CHECK,
            source="risk_engine",
            summary=decision.reason,
            confidence=1.0 if decision.allowed else 0.0,
            payload={"allowed": decision.allowed, "rejections": decision.rejections},
        )

    def _cooldown_active(self, context: RiskContext) -> bool:
        if context.minutes_since_last_loss is None:
            return False
        return context.minutes_since_last_loss < self.cooldown_after_loss_minutes
