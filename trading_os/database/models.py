from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class BaseRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class MarketDataRecord(BaseRecord):
    symbol: str = ""
    source: str = ""
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionRecord(BaseRecord):
    symbol: str = ""
    action: str = "SKIP"
    verified: bool = False
    evidence_count: int = 0
    reason: str = ""


@dataclass(frozen=True)
class JournalRecord(BaseRecord):
    symbol: str = ""
    action: str = ""
    mode: str = "paper"
    notes: str = ""
