from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from trading_os.db.models import BotRuntimeStateRecord, PersistentRecord
from trading_os.db.storage import SQLiteStorage

SECRET_MARKERS = ("key", "secret", "token", "password", "credential")


def json_payload(value: Any) -> Any:
    if is_dataclass(value):
        return json_payload(asdict(value))
    if isinstance(value, dict):
        return {str(key): json_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_payload(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(marker in str(key).lower() for marker in SECRET_MARKERS):
                out[str(key)] = "<redacted>" if item else item
            else:
                out[str(key)] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class TradingOSRepository:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    @classmethod
    def from_database_url(cls, database_url: str) -> "TradingOSRepository":
        return cls(SQLiteStorage(database_url))

    def save_bot_state(self, state: BotRuntimeStateRecord | dict[str, Any]) -> PersistentRecord:
        return self._save("bot_state", state)

    def get_latest_bot_state(self) -> dict[str, Any] | None:
        return self._latest_payload("bot_state")

    def save_portfolio_snapshot(self, snapshot: Any) -> PersistentRecord:
        return self._save("portfolio_snapshot", snapshot)

    def get_latest_portfolio_snapshot(self) -> dict[str, Any] | None:
        return self._latest_payload("portfolio_snapshot")

    def save_open_position(self, position: Any) -> PersistentRecord:
        payload = json_payload(position)
        record_id = str(payload.get("position_id", ""))
        return self._save("open_position", payload, record_id=record_id or None)

    def update_open_position(self, position: Any) -> PersistentRecord:
        return self.save_open_position(position)

    def close_position(self, position: Any) -> PersistentRecord:
        return self._save("closed_position", position)

    def list_open_positions(self) -> list[dict[str, Any]]:
        closed_ids = {
            str(item["payload"].get("position_id", ""))
            for item in self.storage.list_records("closed_position", 500)
        }
        return [
            item["payload"]
            for item in self.storage.list_records("open_position", 500)
            if str(item["payload"].get("position_id", "")) not in closed_ids
            and str(item["payload"].get("status", "OPEN")).upper() != "CLOSED"
        ]

    def list_closed_positions(self) -> list[dict[str, Any]]:
        return [item["payload"] for item in self.storage.list_records("closed_position", 500)]

    def save_trade_journal_entry(self, entry: Any) -> PersistentRecord:
        return self._save("trade_journal_entry", entry)

    def list_trade_journal(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._latest_payloads("trade_journal_entry", limit)

    def save_execution_intent(self, intent: Any) -> PersistentRecord:
        return self._save("execution_intent", intent)

    def save_ai_decision(self, decision: Any) -> PersistentRecord:
        return self._save("ai_decision", decision)

    def list_ai_decisions(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._latest_payloads("ai_decision", limit)

    def save_strategy_signal(self, signal: Any) -> PersistentRecord:
        return self._save("strategy_signal", signal)

    def list_strategy_signals(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("strategy_signal", limit)

    def save_market_intelligence_snapshot(self, snapshot: Any) -> PersistentRecord:
        return self._save("market_intelligence_snapshot", snapshot)

    def list_market_intelligence_snapshots(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("market_intelligence_snapshot", limit)

    def save_risk_result(self, result: Any) -> PersistentRecord:
        return self._save("risk_result", result)

    def list_risk_results(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("risk_result", limit)

    def save_zero_hallucination_result(self, result: Any) -> PersistentRecord:
        return self._save("zero_hallucination_result", result)

    def list_zero_hallucination_results(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("zero_hallucination_result", limit)

    def save_audit_event(self, event: Any) -> PersistentRecord:
        return self._save("audit_event", redact(json_payload(event)))

    def list_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._latest_payloads("audit_event", limit)

    def save_notification_event(self, event: Any) -> PersistentRecord:
        return self._save("notification_event", event)

    def save_license_record(self, record: Any) -> PersistentRecord:
        payload = json_payload(record)
        record_id = str(payload.get("license_id", ""))
        persistent = PersistentRecord(category="license_record", payload=payload)
        if record_id:
            persistent = PersistentRecord(
                category="license_record",
                payload=payload,
                record_id=record_id,
            )
        return self.storage.save_record(persistent)

    def list_license_records(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("license_record", limit)

    def list_execution_intents(self, limit: int = 500) -> list[dict[str, Any]]:
        return self._latest_payloads("execution_intent", limit)

    def list_daily_performance(self, limit: int = 90) -> list[dict[str, Any]]:
        return self._latest_payloads("daily_performance", limit)

    def save_settings(self, key: str, value: dict[str, Any]) -> None:
        safe_value = redact(json_payload(value))
        safe_value["live_trading_enabled"] = False
        safe_value["withdrawals_supported"] = False
        safe_value["margin_futures_enabled"] = False
        self.storage.save_setting(key, safe_value)

    def get_settings(self, key: str) -> dict[str, Any] | None:
        return self.storage.get_setting(key)

    def save_shutdown_state(self, state: Any) -> PersistentRecord:
        return self._save("shutdown_state", state)

    def save_daily_performance(self, summary: Any) -> PersistentRecord:
        return self._save("daily_performance", summary)

    def get_daily_performance(self, day: str) -> dict[str, Any] | None:
        for item in self.storage.list_records("daily_performance", 500, newest_first=True):
            payload = item["payload"]
            if payload.get("date") == day:
                return payload
        return None

    def _save(self, category: str, value: Any, record_id: str | None = None) -> PersistentRecord:
        payload = redact(json_payload(value))
        record = PersistentRecord(category=category, payload=payload)
        if record_id:
            record = PersistentRecord(category=category, payload=payload, record_id=record_id)
        return self.storage.save_record(record)

    def _latest_payload(self, category: str) -> dict[str, Any] | None:
        latest = self.storage.latest_record(category)
        return latest["payload"] if latest else None

    def _latest_payloads(self, category: str, limit: int) -> list[dict[str, Any]]:
        rows = self.storage.list_records(category, limit, newest_first=True)
        rows.reverse()
        return [item["payload"] for item in rows]
