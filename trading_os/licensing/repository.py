from __future__ import annotations

from trading_os.db.repository import TradingOSRepository
from trading_os.licensing.models import LicenseRecord
from trading_os.licensing.validator import hash_license_key


class LicenseRepository:
    def __init__(self, repository: TradingOSRepository) -> None:
        self.repository = repository

    def save(self, record: LicenseRecord) -> LicenseRecord:
        self.repository.save_license_record(record)
        return record

    def list(self, limit: int = 500) -> list[dict[str, object]]:
        return self.repository.list_license_records(limit)

    def get_by_id(self, license_id: str) -> dict[str, object] | None:
        for item in self.list():
            if item.get("license_id") == license_id:
                return item
        return None

    def get_by_key(self, license_key: str) -> dict[str, object] | None:
        key_hash = hash_license_key(license_key)
        for item in self.list():
            if item.get("key_hash") == key_hash:
                return item
        return None
