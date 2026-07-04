from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib

from trading_os.licensing.key_generator import is_valid_key_format, redact_license_key
from trading_os.licensing.models import (
    LicenseRecord,
    LicenseStatus,
    LicenseValidationResult,
    utc_now,
)


def hash_license_key(license_key: str) -> str:
    normalized = license_key.strip().upper()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_expired(expiry_date: str | None) -> bool:
    if not expiry_date:
        return False
    try:
        expiry = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
    except ValueError:
        return True
    return expiry < datetime.now(timezone.utc)


def validate_license_record(
    license_key: str,
    record: LicenseRecord | None,
    package_name: str,
    backend_url: str | None = None,
    device_fingerprint: str | None = None,
) -> LicenseValidationResult:
    redacted = redact_license_key(license_key)
    if not is_valid_key_format(license_key):
        return LicenseValidationResult(False, "INVALID", "License key format is invalid.", redacted_license_key=redacted)
    if record is None:
        return LicenseValidationResult(False, "INVALID", "License key was not found.", redacted_license_key=redacted)
    if record.status != LicenseStatus.ACTIVE:
        return LicenseValidationResult(False, record.status, f"License is {record.status.value}.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    if is_expired(record.expiry_date):
        return LicenseValidationResult(False, LicenseStatus.EXPIRED, "License is expired.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    if record.activation_count > record.device_limit:
        return LicenseValidationResult(False, "DEVICE_LIMIT_REACHED", "Device activation limit reached.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    if record.allowed_app_package and record.allowed_app_package != package_name:
        return LicenseValidationResult(False, "PACKAGE_NOT_ALLOWED", "App package is not allowed.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    if record.backend_url_binding and backend_url and record.backend_url_binding != backend_url:
        return LicenseValidationResult(False, "BACKEND_URL_MISMATCH", "Backend URL binding mismatch.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    if record.device_fingerprint_binding and device_fingerprint and record.device_fingerprint_binding != device_fingerprint:
        return LicenseValidationResult(False, "DEVICE_MISMATCH", "Device fingerprint binding mismatch.", record.license_type, record.expiry_date, 0, redacted_license_key=redacted, license_id=record.license_id)
    remaining = max(record.device_limit - record.activation_count, 0)
    return LicenseValidationResult(True, record.status, "License is valid.", record.license_type, record.expiry_date, remaining, redacted_license_key=redacted, license_id=record.license_id)


def mark_validated(record: LicenseRecord, increment_activation: bool = True) -> LicenseRecord:
    return replace(
        record,
        activation_count=record.activation_count + (1 if increment_activation else 0),
        last_validation_at=utc_now(),
        updated_at=utc_now(),
    )
