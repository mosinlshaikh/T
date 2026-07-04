from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from time import sleep
from typing import Callable

from trading_os.audit.audit_logger import AuditLogger
from trading_os.config import RuntimeMode, TradingOSConfig
from trading_os.db.models import BotRuntimeStateRecord
from trading_os.db.repository import TradingOSRepository
from trading_os.runtime.bot_state import BotState
from trading_os.runtime.shutdown_engine import ShutdownState, SmartShutdownEngine
from trading_os.security.api_key_vault import ApiKeyVaultDesign
from trading_os.security.permission_verifier import (
    ApiReadinessStatus,
    BinanceApiPermissionVerifier,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class FailureState(str, Enum):
    NONE = "NONE"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    BINANCE_CONNECTION_FAILURE = "BINANCE_CONNECTION_FAILURE"
    CRASH_GUARD_TRIGGERED = "CRASH_GUARD_TRIGGERED"


@dataclass(frozen=True)
class Heartbeat:
    state: BotState
    healthy: bool
    timestamp: str = field(default_factory=utc_now)
    failure_state: FailureState = FailureState.NONE
    message: str = ""


@dataclass
class RetryBackoff:
    base_seconds: float = 1.0
    max_seconds: float = 60.0
    attempts: int = 0

    def next_delay(self) -> float:
        delay = min(self.base_seconds * (2**self.attempts), self.max_seconds)
        self.attempts += 1
        return delay

    def reset(self) -> None:
        self.attempts = 0


@dataclass
class RuntimeSupervisor:
    config: TradingOSConfig
    vault: ApiKeyVaultDesign
    permission_verifier: BinanceApiPermissionVerifier
    shutdown: SmartShutdownEngine
    audit: AuditLogger
    repository: TradingOSRepository | None = None
    state: BotState = BotState.BOOTING
    failure_state: FailureState = FailureState.NONE
    healthy: bool = False
    heartbeat_count: int = 0
    backoff: RetryBackoff = field(default_factory=RetryBackoff)
    last_error: str = ""

    def boot(self) -> BotState:
        self.restore_state()
        if self.state == BotState.EMERGENCY_STOPPED:
            return self.state
        self._set_state(BotState.CONFIG_CHECK)
        validation = self.config.validate()
        self.audit.log_config_validation_result(
            {
                "valid": validation.valid,
                "errors": validation.errors,
                "warnings": validation.warnings,
            }
        )
        if not validation.valid:
            self.healthy = False
            return self._error("; ".join(validation.errors))

        self._set_state(BotState.VAULT_CHECK)
        vault_health = self.vault.health_report()
        self.audit.log_secret_availability_status(vault_health)

        self._set_state(BotState.API_PERMISSION_CHECK)
        readiness = self.permission_verifier.verify(self.config, self.vault)
        self.audit.log_api_readiness_result(
            {
                "status": readiness.status.value,
                "ready": readiness.ready,
                "reasons": readiness.reasons,
            }
        )
        if readiness.status == ApiReadinessStatus.LIVE_BLOCKED:
            self.healthy = False
            return self._set_state(BotState.LIVE_BLOCKED)
        if readiness.status in {
            ApiReadinessStatus.MISCONFIGURED,
            ApiReadinessStatus.SECRET_MISSING,
        }:
            self.healthy = False
            return self._error("; ".join(readiness.reasons))

        self.healthy = True
        if self.config.runtime_mode == RuntimeMode.SANDBOX:
            return self._set_state(BotState.SANDBOX_READY)
        return self._set_state(BotState.PAPER_READY)

    def start(self) -> BotState:
        if self.state not in {BotState.PAPER_READY, BotState.SANDBOX_READY}:
            self.boot()
        if not self.healthy:
            return self.state
        return self._set_state(BotState.RUNNING)

    def run_once(self, work: Callable[[], None] | None = None) -> Heartbeat:
        if self.state != BotState.RUNNING:
            self.start()
        if not self.healthy or self.state != BotState.RUNNING:
            return self.heartbeat("Supervisor is not healthy; trade execution remains blocked.")
        try:
            if work is not None:
                work()
            self.failure_state = FailureState.NONE
            self.backoff.reset()
            return self.heartbeat("Runtime loop tick completed.")
        except ConnectionError as exc:
            self.failure_state = FailureState.NETWORK_FAILURE
            self.healthy = False
            self.audit.log_reconnect_attempt(
                {"failure_state": self.failure_state.value, "reason": str(exc)}
            )
            self._set_state(BotState.DEGRADED)
            return self.heartbeat("Network failure; reconnect required.")
        except RuntimeError as exc:
            self.failure_state = FailureState.BINANCE_CONNECTION_FAILURE
            self.healthy = False
            self.audit.log_reconnect_attempt(
                {"failure_state": self.failure_state.value, "reason": str(exc)}
            )
            self._set_state(BotState.DEGRADED)
            return self.heartbeat("Binance connection failure; reconnect required.")
        except Exception as exc:
            self.failure_state = FailureState.CRASH_GUARD_TRIGGERED
            self.healthy = False
            self.last_error = str(exc)
            self._set_state(BotState.ERROR)
            return self.heartbeat("Crash guard triggered.")

    def run_forever(
        self,
        work: Callable[[], None] | None = None,
        max_iterations: int | None = None,
    ) -> None:
        iterations = 0
        self.start()
        while self.state == BotState.RUNNING:
            self.run_once(work)
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            sleep(self.backoff.next_delay())

    def reconnect(self) -> BotState:
        delay = self.backoff.next_delay()
        self.audit.log_reconnect_attempt(
            {"failure_state": self.failure_state.value, "delay_seconds": delay}
        )
        self.healthy = True
        self.failure_state = FailureState.NONE
        return self._set_state(BotState.RUNNING)

    def request_stop(self, active_trade_count: int = 0) -> BotState:
        self._set_state(BotState.SHUTDOWN_REQUESTED)
        shutdown_state = self.shutdown.request_shutdown(active_trade_count)
        if shutdown_state == ShutdownState.SAVING_LOGS:
            self.shutdown.logs_saved()
            self.healthy = False
            return self._set_state(BotState.SAFELY_STOPPED)
        self.healthy = False
        return self.state

    def emergency_stop(self, reason: str) -> BotState:
        self.shutdown.emergency_stop(reason)
        self.healthy = False
        self.failure_state = FailureState.CRASH_GUARD_TRIGGERED
        return self._set_state(BotState.EMERGENCY_STOPPED)

    def heartbeat(self, message: str = "") -> Heartbeat:
        self.heartbeat_count += 1
        heartbeat = Heartbeat(
            state=self.state,
            healthy=self.healthy,
            failure_state=self.failure_state,
            message=message,
        )
        self.audit.log_runtime_heartbeat(
            {
                "state": heartbeat.state.value,
                "healthy": heartbeat.healthy,
                "failure_state": heartbeat.failure_state.value,
                "message": heartbeat.message,
                "count": self.heartbeat_count,
            }
        )
        return heartbeat

    def restore_state(self) -> None:
        if self.repository is None:
            return
        latest = self.repository.get_latest_bot_state()
        if not latest:
            return
        previous_state = str(latest.get("state", ""))
        open_positions = int(latest.get("open_paper_positions", 0) or 0)
        interrupted = bool(latest.get("interrupted_shutdown", False))
        if previous_state == BotState.EMERGENCY_STOPPED.value:
            self.state = BotState.EMERGENCY_STOPPED
            self.healthy = False
            self.last_error = "Previous runtime was emergency stopped; manual review required."
        elif open_positions > 0 or interrupted:
            self.state = BotState.DEGRADED
            self.healthy = False
            self.last_error = (
                "Previous runtime had active/interrupted paper state; management resume required."
            )

    @property
    def permits_trade_execution(self) -> bool:
        return self.healthy and self.state == BotState.RUNNING

    def _error(self, reason: str) -> BotState:
        self.last_error = reason
        return self._set_state(BotState.ERROR)

    def _set_state(self, state: BotState) -> BotState:
        previous = self.state
        self.state = state
        self.audit.log_supervisor_state_change({"from": previous.value, "to": state.value})
        if self.repository is not None:
            self.repository.save_bot_state(
                BotRuntimeStateRecord(
                    state=state.value,
                    shutdown_state=self.shutdown.state.value,
                    healthy=self.healthy,
                    failure_state=self.failure_state.value,
                    open_paper_positions=0,
                    interrupted_shutdown=state
                    in {BotState.DEGRADED, BotState.SHUTDOWN_REQUESTED, BotState.ERROR},
                )
            )
        return state
