from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LicenseType(str, Enum):
    OWNER = "OWNER"
    INTERNAL_TEST = "INTERNAL_TEST"
    CLIENT_TRIAL = "CLIENT_TRIAL"
    CLIENT_MONTHLY = "CLIENT_MONTHLY"
    CLIENT_YEARLY = "CLIENT_YEARLY"
    CLIENT_LIFETIME = "CLIENT_LIFETIME"


class LicenseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"


@dataclass(frozen=True)
class LicenseRecord:
    license_id: str
    key_hash: str
    license_type: LicenseType
    status: LicenseStatus
    device_limit: int
    activation_count: int
    allowed_app_package: str
    client_name: str
    client_email: str = ""
    notes: str = ""
    expiry_date: str | None = None
    backend_url_binding: str | None = None
    device_fingerprint_binding: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    revoked_at: str | None = None
    last_validation_at: str | None = None


@dataclass(frozen=True)
class LicenseCreationResult:
    full_license_key: str
    record: LicenseRecord
    warning: str = "Show this full license key only once. Store only hashed keys."


@dataclass(frozen=True)
class LicenseValidationResult:
    valid: bool
    status: LicenseStatus | str
    message: str
    license_type: LicenseType | str = ""
    expiry_date: str | None = None
    remaining_activations: int = 0
    warnings: list[str] = field(default_factory=list)
    redacted_license_key: str = ""
    license_id: str = ""


def new_license_id() -> str:
    return str(uuid4())
