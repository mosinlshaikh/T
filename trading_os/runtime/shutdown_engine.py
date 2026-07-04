from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from trading_os.execution.intent import OrderIntentType


class ShutdownState(str, Enum):
    RUNNING = "RUNNING"
    SHUTDOWN_REQUESTED = "SHUTDOWN_REQUESTED"
    FINISHING_ACTIVE_TRADES = "FINISHING_ACTIVE_TRADES"
    SAVING_LOGS = "SAVING_LOGS"
    SAFELY_STOPPED = "SAFELY_STOPPED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"


@dataclass
class SmartShutdownEngine:
    state: ShutdownState = ShutdownState.RUNNING
    state_log: list[ShutdownState] = field(default_factory=lambda: [ShutdownState.RUNNING])

    def request_shutdown(self, active_trade_count: int) -> ShutdownState:
        self._set_state(ShutdownState.SHUTDOWN_REQUESTED)
        if active_trade_count > 0:
            return self._set_state(ShutdownState.FINISHING_ACTIVE_TRADES)
        return self._set_state(ShutdownState.SAVING_LOGS)

    def active_trades_safe(self, active_trade_count: int = 0) -> ShutdownState:
        if self.state != ShutdownState.FINISHING_ACTIVE_TRADES:
            return self.state
        if active_trade_count > 0:
            return self.state
        return self._set_state(ShutdownState.SAVING_LOGS)

    def logs_saved(self) -> ShutdownState:
        if self.state != ShutdownState.SAVING_LOGS:
            return self.state
        return self._set_state(ShutdownState.SAFELY_STOPPED)

    def emergency_stop(self, reason: str = "") -> ShutdownState:
        return self._set_state(ShutdownState.EMERGENCY_STOPPED)

    @property
    def accepts_new_trades(self) -> bool:
        return self.state == ShutdownState.RUNNING

    @property
    def must_manage_active_trades(self) -> bool:
        return self.state in {
            ShutdownState.RUNNING,
            ShutdownState.SHUTDOWN_REQUESTED,
            ShutdownState.FINISHING_ACTIVE_TRADES,
        }

    @property
    def stop_loss_take_profit_must_remain_active(self) -> bool:
        return self.state != ShutdownState.EMERGENCY_STOPPED

    def allows_new_trade_intent(self) -> bool:
        return self.state == ShutdownState.RUNNING

    def allows_exit_intent(self, intent_type: OrderIntentType) -> bool:
        if self.state == ShutdownState.EMERGENCY_STOPPED:
            return False
        return intent_type in {
            OrderIntentType.MARKET_SELL,
            OrderIntentType.STOP_LOSS,
            OrderIntentType.TAKE_PROFIT,
            OrderIntentType.PARTIAL_EXIT,
        }

    def can_safely_stop(self, active_trade_count: int) -> bool:
        return active_trade_count == 0 and self.state in {
            ShutdownState.SAVING_LOGS,
            ShutdownState.SAFELY_STOPPED,
        }

    def _set_state(self, state: ShutdownState) -> ShutdownState:
        self.state = state
        self.state_log.append(state)
        return state
