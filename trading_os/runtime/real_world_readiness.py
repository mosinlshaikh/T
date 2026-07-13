from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_os.config import TradingOSConfig
from trading_os.learning.local_ai_engine import LocalAIMarketKingEngine
from trading_os.risk.risk_engine import RiskEngine
from trading_os.security.api_key_vault import ApiKeyVaultDesign
from trading_os.security.kill_switch import EmergencyKillSwitch
from trading_os.security.permission_verifier import BinanceApiPermissionVerifier


@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    passed: bool
    status: str
    reason: str


@dataclass(frozen=True)
class RealWorldReadinessReport:
    status: str
    ready_for_paper: bool
    ready_for_real_money: bool
    live_execution_available: bool
    trading_mode: str
    checks: list[ReadinessCheck] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    safety_statement: str = ""


@dataclass
class RealWorldReadinessGate:
    config: TradingOSConfig
    vault: ApiKeyVaultDesign
    permission_verifier: BinanceApiPermissionVerifier
    risk_engine: RiskEngine
    kill_switch: EmergencyKillSwitch
    local_ai: LocalAIMarketKingEngine

    def evaluate(self) -> RealWorldReadinessReport:
        api = self.permission_verifier.verify(self.config, self.vault)
        local_ai_snapshot = self.local_ai.snapshot()

        checks = [
            ReadinessCheck(
                "paper_mode_default",
                self.config.runtime_mode.value in {"paper", "sandbox"},
                self.config.runtime_mode.value,
                "Backend must remain paper/sandbox until a separate audited live phase.",
            ),
            ReadinessCheck(
                "live_trading_disabled",
                not self.config.enable_live_trading,
                str(self.config.enable_live_trading).lower(),
                "Live trading remains blocked in this build.",
            ),
            ReadinessCheck(
                "manual_live_unlock_disabled",
                not self.config.manual_live_unlock,
                str(self.config.manual_live_unlock).lower(),
                "Manual live unlock must remain false in this build.",
            ),
            ReadinessCheck(
                "withdrawals_blocked",
                not self.config.allow_withdraw_permissions,
                str(self.config.allow_withdraw_permissions).lower(),
                "Withdraw permissions are unsupported.",
            ),
            ReadinessCheck(
                "api_readiness",
                api.ready,
                api.status.value,
                "; ".join(api.reasons) or "API readiness checked safely.",
            ),
            ReadinessCheck(
                "kill_switch_clear",
                not self.kill_switch.active,
                "active" if self.kill_switch.active else "clear",
                "Emergency stop must be clear for paper operation.",
            ),
            ReadinessCheck(
                "risk_policy_configured",
                self._risk_policy_safe(),
                "configured",
                "Reserve, exposure, loss limit, SL, and TP rules are present.",
            ),
            ReadinessCheck(
                "local_ai_learning",
                local_ai_snapshot.status in {"ok", "insufficient_data"},
                str(local_ai_snapshot.status),
                "Local AI is advisory only and uses persisted paper evidence.",
            ),
        ]

        blockers = [
            check.reason for check in checks if not check.passed and check.name != "api_readiness"
        ]
        if self.config.enable_live_trading:
            blockers.append("Live trading flag must not be true in this build.")
        if self.config.manual_live_unlock:
            blockers.append("Manual live unlock must not be true in this build.")

        ready_for_paper = all(
            check.passed
            for check in checks
            if check.name
            in {
                "paper_mode_default",
                "live_trading_disabled",
                "manual_live_unlock_disabled",
                "withdrawals_blocked",
                "kill_switch_clear",
                "risk_policy_configured",
                "local_ai_learning",
            }
        )

        return RealWorldReadinessReport(
            status="PAPER_READY" if ready_for_paper else "BLOCKED",
            ready_for_paper=ready_for_paper,
            ready_for_real_money=False,
            live_execution_available=False,
            trading_mode=self.config.runtime_mode.value,
            checks=checks,
            blockers=blockers or ["Real-money execution is intentionally not available."],
            next_steps=self._next_steps(local_ai_snapshot.status),
            safety_statement=(
                "This build can be used for paper testing and readiness review only. "
                "It must not place real Binance orders."
            ),
        )

    def _risk_policy_safe(self) -> bool:
        return (
            self.risk_engine.reserve_capital_pct >= 10.0
            and self.risk_engine.max_risk_exposure_pct <= 5.0
            and self.risk_engine.max_trade_size > 0
            and self.risk_engine.daily_loss_limit_pct > 0
            and self.risk_engine.consecutive_loss_limit > 0
        )

    @staticmethod
    def _next_steps(local_ai_status: str) -> list[str]:
        steps = [
            "Collect more paper decisions through /control/paper-auto-trader/scan.",
            "Review /learning/market-king-score before increasing confidence.",
            "Keep emergency stop tested before every public demo.",
            "Validate Android dashboard against the deployed backend.",
        ]
        if local_ai_status == "insufficient_data":
            steps.insert(0, "Run a longer paper session to build local AI evidence memory.")
        return steps


def report_to_dict(report: RealWorldReadinessReport) -> dict[str, Any]:
    return {
        "status": report.status,
        "ready_for_paper": report.ready_for_paper,
        "ready_for_real_money": report.ready_for_real_money,
        "live_execution_available": report.live_execution_available,
        "trading_mode": report.trading_mode,
        "checks": [check.__dict__ for check in report.checks],
        "blockers": report.blockers,
        "next_steps": report.next_steps,
        "safety_statement": report.safety_statement,
    }
