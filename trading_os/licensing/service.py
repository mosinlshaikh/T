from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from trading_os.licensing.key_generator import generate_license_key, redact_license_key
from trading_os.licensing.models import (
    LicenseCreationResult,
    LicenseRecord,
    LicenseStatus,
    LicenseType,
    LicenseValidationResult,
    new_license_id,
    utc_now,
)
from trading_os.licensing.repository import LicenseRepository
from trading_os.licensing.validator import (
    hash_license_key,
    mark_validated,
    validate_license_record,
)

DEFAULT_PACKAGE = "com.ttechnologyresearchlab.tradingos"


class LicenseService:
    def __init__(self, repository: LicenseRepository) -> None:
        self.repository = repository

    def generate(
        self,
        license_type: LicenseType,
        client_name: str,
        client_email: str = "",
        notes: str = "",
        expiry_date: str | None = None,
        device_limit: int = 1,
        allowed_app_package: str = DEFAULT_PACKAGE,
        backend_url_binding: str | None = None,
        device_fingerprint_binding: str | None = None,
    ) -> LicenseCreationResult:
        full_key = generate_license_key()
        record = LicenseRecord(
            license_id=new_license_id(),
            key_hash=hash_license_key(full_key),
            license_type=license_type,
            status=LicenseStatus.ACTIVE,
            device_limit=max(device_limit, 1),
            activation_count=0,
            allowed_app_package=allowed_app_package,
            client_name=client_name,
            client_email=client_email,
            notes=notes,
            expiry_date=expiry_date,
            backend_url_binding=backend_url_binding,
            device_fingerprint_binding=device_fingerprint_binding,
        )
        self.repository.save(record)
        return LicenseCreationResult(full_key, record)

    def validate(
        self,
        license_key: str,
        package_name: str = DEFAULT_PACKAGE,
        backend_url: str | None = None,
        device_fingerprint: str | None = None,
    ) -> LicenseValidationResult:
        raw = self.repository.get_by_key(license_key)
        record = self._record_from_payload(raw) if raw else None
        result = validate_license_record(
            license_key, record, package_name, backend_url, device_fingerprint
        )
        if result.valid and record is not None:
            should_increment = (
                record.last_validation_at is None and record.activation_count < record.device_limit
            )
            self.repository.save(mark_validated(record, increment_activation=should_increment))
        return result

    def set_status(self, license_id: str, status: LicenseStatus) -> dict[str, object] | None:
        raw = self.repository.get_by_id(license_id)
        if raw is None:
            return None
        record = self._record_from_payload(raw)
        updated = replace(
            record,
            status=status,
            updated_at=utc_now(),
            revoked_at=utc_now() if status == LicenseStatus.REVOKED else record.revoked_at,
        )
        self.repository.save(updated)
        return self.redacted_record(asdict(updated))

    @staticmethod
    def redacted_record(payload: dict[str, Any]) -> dict[str, Any]:
        redacted = dict(payload)
        if redacted.get("key_hash"):
            redacted["key_hash"] = "<hashed>"
        redacted["license_key"] = redact_license_key(str(redacted.get("license_key", "")))
        return redacted

    @staticmethod
    def _record_from_payload(payload: dict[str, object]) -> LicenseRecord:
        data = dict(payload)
        data["license_type"] = LicenseType(str(data["license_type"]))
        data["status"] = LicenseStatus(str(data["status"]))
        return LicenseRecord(**data)
