from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class JournalEntry:
    symbol: str
    action: str
    mode: str
    reason: str
    trade_id: str = ""
    intent_id: str = ""
    quantity: float = 0.0
    price: float = 0.0
    realized_pnl: float = 0.0
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TradeJournal:
    entries: list[JournalEntry] = field(default_factory=list)

    def record(self, entry: JournalEntry) -> JournalEntry:
        self.entries.append(entry)
        return entry
