from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from trading_os.config import TradingOSConfig
from trading_os.db.repository import TradingOSRepository
from trading_os.runtime.bot_state import BotState
from trading_os.security.api_key_vault import ApiKeyVaultDesign


class SafetyLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGER = "DANGER"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SafetyScore:
    score: int
    level: SafetyLevel
    reasons: list[str] = field(default_factory=list)
    recommended_action: str = "Continue paper-only monitoring."


@dataclass
class SafetyScoreEngine:
    repository: TradingOSRepository
    config: TradingOSConfig
    vault: ApiKeyVaultDesign
    emergency_state: str = ""

    def calculate(self) -> SafetyScore:
        score = 100
        reasons: list[str] = []
        if self.config.enable_live_trading:
            score -= 50
            reasons.append("Live trading is enabled, which is not allowed in this phase.")
        else:
            reasons.append("Live trading is disabled.")
        if self.config.allow_withdraw_permissions:
            score -= 50
            reasons.append("Withdrawals are enabled, which is forbidden.")
        else:
            reasons.append("Withdrawals are unsupported.")

        audit = self.repository.list_audit_events(500)
        missing_skips = len(
            [
                item
                for item in audit
                if item.get("event_type") == "skipped_trade"
                and "missing" in str(item.get("payload", {})).lower()
            ]
        )
        risk_rejections = len(
            [item for item in audit if item.get("event_type") == "risk_rejection"]
        )
        hallucination_blocks = len(
            [item for item in audit if item.get("event_type") == "blocked_hallucination"]
        )
        score += min(risk_rejections, 5)
        score += min(hallucination_blocks, 5)
        score -= min(missing_skips, 10)
        if self.emergency_state == BotState.EMERGENCY_STOPPED.value:
            score -= 35
            reasons.append("Emergency stop is active or was restored.")

        vault_health = self.vault.health_report()
        if not vault_health.get("credential_pair_available", False):
            reasons.append("API credential pair is unavailable; paper mode remains acceptable.")

        evidence_quality = self._evidence_quality()
        if evidence_quality == "missing":
            score -= 10
            reasons.append("Persisted evidence history is missing.")
        elif evidence_quality == "partial":
            score -= 5
            reasons.append("Persisted evidence history is partial.")
        else:
            reasons.append("Persisted evidence history is available.")

        score = max(min(score, 100), 0)
        if not audit and evidence_quality == "missing":
            level = SafetyLevel.UNKNOWN
            recommended = "Collect more paper-mode evidence before relying on analytics."
        elif score >= 80:
            level = SafetyLevel.SAFE
            recommended = "Continue paper-only monitoring."
        elif score >= 50:
            level = SafetyLevel.CAUTION
            recommended = "Review missing data, risk rejections, and runtime state."
        else:
            level = SafetyLevel.DANGER
            recommended = "Keep bot stopped and review safety configuration."

        return SafetyScore(score, level, reasons, recommended)

    def _evidence_quality(self) -> str:
        decisions = self.repository.list_ai_decisions(50)
        if not decisions:
            return "missing"
        with_evidence = [item for item in decisions if item.get("evidence")]
        if len(with_evidence) == len(decisions):
            return "complete"
        return "partial"
