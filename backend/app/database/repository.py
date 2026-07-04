from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.database.models import StoredRecord


@dataclass
class InMemoryRepository:
    records: list[StoredRecord] = field(default_factory=list)

    def save(self, category: str, payload: dict[str, object]) -> StoredRecord:
        record = StoredRecord(category=category, payload=payload)
        self.records.append(record)
        return record

    def list(self, category: str) -> list[StoredRecord]:
        return [record for record in self.records if record.category == category]
