from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from trading_os.db.repository import TradingOSRepository


class AuditEventType(str, Enum):
    MARKET_SNAPSHOT = "market_snapshot"
    SIGNAL = "signal"
    AI_DECISION = "ai_decision"
    SKIPPED_TRADE = "skipped_trade"
    BLOCKED_HALLUCINATION = "blocked_hallucination"
    RISK_REJECTION = "risk_rejection"
    ORDER_INTENT = "order_intent"
    SHUTDOWN_STATE_CHANGE = "shutdown_state_change"
    TRADE_LIFECYCLE_TRANSITION = "trade_lifecycle_transition"
    EXECUTION_INTENT_CREATED = "execution_intent_created"
    PAPER_ORDER_FILL = "paper_order_fill"
    PARTIAL_EXIT = "partial_exit"
    STOP_LOSS_EVENT = "stop_loss_event"
    TAKE_PROFIT_EVENT = "take_profit_event"
    PORTFOLIO_SNAPSHOT = "portfolio_snapshot"
    STRATEGY_SIGNAL = "strategy_signal"
    PIPELINE_RESULT = "decision_to_trade_pipeline_result"
    CANDLE_ANALYSIS = "candle_analysis"
    ORDER_BOOK_ANALYSIS = "order_book_analysis"
    WHALE_ANALYSIS = "whale_analysis"
    NEWS_RISK_ANALYSIS = "news_risk_analysis"
    MARKET_STRUCTURE_ANALYSIS = "market_structure_analysis"
    COMBINED_SIGNAL_RESULT = "combined_signal_result"
    MISSING_DATA = "missing_data"
    CONFLICT_REASON = "conflict_reason"
    CONFIG_VALIDATION_RESULT = "config_validation_result"
    SECRET_AVAILABILITY_STATUS = "secret_availability_status"
    API_READINESS_RESULT = "api_readiness_result"
    RUNTIME_HEARTBEAT = "runtime_heartbeat"
    SUPERVISOR_STATE_CHANGE = "supervisor_state_change"
    RECONNECT_ATTEMPT = "reconnect_attempt"
    NOTIFICATION_DISPATCH_RESULT = "notification_dispatch_result"
    HEALTH_SNAPSHOT = "health_snapshot"


@dataclass(frozen=True)
class AuditEvent:
    event_type: str | AuditEventType
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AuditLogger:
    path: str = "data/audit/trading_os_audit.jsonl"
    repository: "TradingOSRepository | None" = None

    def append(self, event: AuditEvent) -> str:
        out = Path(self.path)
        out.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(event)
        if isinstance(event.event_type, AuditEventType):
            data["event_type"] = event.event_type.value
        data["payload"] = self._json_ready(data["payload"])
        with out.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, sort_keys=True) + "\n")
        if self.repository is not None:
            self.repository.save_audit_event(data)
        return event.event_id

    def log(self, event_type: AuditEventType | str, payload: dict[str, Any]) -> str:
        value = event_type.value if isinstance(event_type, AuditEventType) else event_type
        return self.append(AuditEvent(event_type=value, payload=payload))

    def log_market_snapshot(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.MARKET_SNAPSHOT, payload)

    def log_signal(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.SIGNAL, payload)

    def log_ai_decision(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_ai_decision(payload)
        return self.log(AuditEventType.AI_DECISION, payload)

    def log_skipped_trade(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.SKIPPED_TRADE, payload)

    def log_blocked_hallucination(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.BLOCKED_HALLUCINATION, payload)

    def log_risk_rejection(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.RISK_REJECTION, payload)

    def log_order_intent(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.ORDER_INTENT, payload)

    def log_shutdown_state_change(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.SHUTDOWN_STATE_CHANGE, payload)

    def log_trade_lifecycle_transition(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.TRADE_LIFECYCLE_TRANSITION, payload)

    def log_execution_intent_created(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_execution_intent(payload)
        return self.log(AuditEventType.EXECUTION_INTENT_CREATED, payload)

    def log_paper_order_fill(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.PAPER_ORDER_FILL, payload)

    def log_partial_exit(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.PARTIAL_EXIT, payload)

    def log_stop_loss_event(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.STOP_LOSS_EVENT, payload)

    def log_take_profit_event(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.TAKE_PROFIT_EVENT, payload)

    def log_portfolio_snapshot(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_portfolio_snapshot(payload)
        return self.log(AuditEventType.PORTFOLIO_SNAPSHOT, payload)

    def log_strategy_signal(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_strategy_signal(payload)
        return self.log(AuditEventType.STRATEGY_SIGNAL, payload)

    def log_pipeline_result(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.PIPELINE_RESULT, payload)

    def log_candle_analysis(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_market_intelligence_snapshot(payload)
        return self.log(AuditEventType.CANDLE_ANALYSIS, payload)

    def log_order_book_analysis(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_market_intelligence_snapshot(payload)
        return self.log(AuditEventType.ORDER_BOOK_ANALYSIS, payload)

    def log_whale_analysis(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_market_intelligence_snapshot(payload)
        return self.log(AuditEventType.WHALE_ANALYSIS, payload)

    def log_news_risk_analysis(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_market_intelligence_snapshot(payload)
        return self.log(AuditEventType.NEWS_RISK_ANALYSIS, payload)

    def log_market_structure_analysis(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_market_intelligence_snapshot(payload)
        return self.log(AuditEventType.MARKET_STRUCTURE_ANALYSIS, payload)

    def log_combined_signal_result(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.COMBINED_SIGNAL_RESULT, payload)

    def log_missing_data(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.MISSING_DATA, payload)

    def log_conflict_reason(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.CONFLICT_REASON, payload)

    def log_config_validation_result(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.CONFIG_VALIDATION_RESULT, payload)

    def log_secret_availability_status(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.SECRET_AVAILABILITY_STATUS, payload)

    def log_api_readiness_result(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.API_READINESS_RESULT, payload)

    def log_runtime_heartbeat(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.RUNTIME_HEARTBEAT, payload)

    def log_supervisor_state_change(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.SUPERVISOR_STATE_CHANGE, payload)

    def log_reconnect_attempt(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.RECONNECT_ATTEMPT, payload)

    def log_notification_dispatch_result(self, payload: dict[str, Any]) -> str:
        if self.repository is not None:
            self.repository.save_notification_event(payload)
        return self.log(AuditEventType.NOTIFICATION_DISPATCH_RESULT, payload)

    def log_health_snapshot(self, payload: dict[str, Any]) -> str:
        return self.log(AuditEventType.HEALTH_SNAPSHOT, payload)

    def _json_ready(self, value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {str(key): self._json_ready(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_ready(item) for item in value]
        if isinstance(value, tuple):
            return [self._json_ready(item) for item in value]
        return value
