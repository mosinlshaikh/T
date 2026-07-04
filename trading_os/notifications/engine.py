from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from trading_os.audit.audit_logger import AuditLogger


class NotificationEventType(str, Enum):
    BOT_STARTED = "BOT_STARTED"
    BOT_STOPPED = "BOT_STOPPED"
    TRADE_SIGNAL = "TRADE_SIGNAL"
    TRADE_SKIPPED = "TRADE_SKIPPED"
    RISK_REJECTED = "RISK_REJECTED"
    HALLUCINATION_BLOCKED = "HALLUCINATION_BLOCKED"
    SHUTDOWN_REQUESTED = "SHUTDOWN_REQUESTED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class NotificationMessage:
    event_type: NotificationEventType
    title: str
    body: str
    metadata: dict[str, object] = field(default_factory=dict)

    def sanitized(self) -> "NotificationMessage":
        blocked = {"key", "secret", "token", "password"}
        metadata = {
            key: ("<redacted>" if any(part in key.lower() for part in blocked) else value)
            for key, value in self.metadata.items()
        }
        return NotificationMessage(self.event_type, self.title, self.body, metadata)


class NotificationAdapter:
    name: str

    def dispatch(self, message: NotificationMessage) -> bool:
        raise NotImplementedError


@dataclass
class TelegramNotificationAdapter(NotificationAdapter):
    name: str = "telegram"
    enabled: bool = False

    def dispatch(self, message: NotificationMessage) -> bool:
        return self.enabled


@dataclass
class WhatsAppNotificationAdapter(NotificationAdapter):
    name: str = "whatsapp"
    enabled: bool = False

    def dispatch(self, message: NotificationMessage) -> bool:
        return self.enabled


@dataclass
class EmailNotificationAdapter(NotificationAdapter):
    name: str = "email"
    enabled: bool = False

    def dispatch(self, message: NotificationMessage) -> bool:
        return self.enabled


@dataclass
class NotificationDispatchResult:
    event_type: NotificationEventType
    adapter_results: dict[str, bool]


@dataclass
class NotificationEngine:
    audit: AuditLogger | None = None
    adapters: list[NotificationAdapter] = field(
        default_factory=lambda: [
            TelegramNotificationAdapter(),
            WhatsAppNotificationAdapter(),
            EmailNotificationAdapter(),
        ]
    )

    def dispatch(self, message: NotificationMessage) -> NotificationDispatchResult:
        sanitized = message.sanitized()
        result = NotificationDispatchResult(
            event_type=sanitized.event_type,
            adapter_results={
                adapter.name: adapter.dispatch(sanitized) for adapter in self.adapters
            },
        )
        if self.audit is not None:
            self.audit.log_notification_dispatch_result(
                {
                    "event_type": result.event_type.value,
                    "adapter_results": result.adapter_results,
                }
            )
        return result
