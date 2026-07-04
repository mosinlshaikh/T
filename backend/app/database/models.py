from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class StoredRecord:
    category: str
    payload: dict[str, object]
    record_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=now)
