from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend

_backend: TradingOSBackend | None = None


def get_backend() -> TradingOSBackend:
    global _backend
    if _backend is None:
        _backend = TradingOSBackend(config=TradingOSConfig.from_env())
    return _backend


def set_backend(backend: TradingOSBackend) -> None:
    global _backend
    _backend = backend


def position_payload(position: object) -> dict[str, Any]:
    return asdict(position)


def latest_audit_events(limit: int = 50, event_type: str | None = None) -> list[dict[str, Any]]:
    backend = get_backend()
    persisted = backend.repository.list_audit_events(limit=max(limit * 3, limit))
    if persisted:
        if event_type is not None:
            persisted = [item for item in persisted if item.get("event_type") == event_type]
        return persisted[-limit:]
    path = Path(backend.config.audit_log_path)
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-max(limit * 3, limit) :]:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event_type is None or event.get("event_type") == event_type:
            events.append(event)
    return events[-limit:]


def latest_decisions(limit: int = 20) -> list[dict[str, Any]]:
    backend = get_backend()
    persisted = backend.repository.list_ai_decisions(limit=limit)
    if persisted:
        return persisted
    return latest_audit_events(limit=limit, event_type="ai_decision")
