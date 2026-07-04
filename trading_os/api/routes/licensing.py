from __future__ import annotations

from dataclasses import asdict, dataclass
import os

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import fail, ok
from trading_os.licensing import key_generator
from trading_os.licensing.models import LicenseStatus, LicenseType
from trading_os.licensing.repository import LicenseRepository
from trading_os.licensing.service import DEFAULT_PACKAGE, LicenseService

router = APIRouter(tags=["licensing"])


@dataclass
class GenerateLicenseRequest:
    license_type: str = LicenseType.CLIENT_TRIAL.value
    client_name: str = ""
    client_email: str = ""
    notes: str = ""
    expiry_date: str | None = None
    device_limit: int = 1
    allowed_app_package: str = DEFAULT_PACKAGE
    backend_url_binding: str | None = None
    device_fingerprint_binding: str | None = None
    admin_token: str = ""


@dataclass
class AdminTokenRequest:
    admin_token: str = ""


@dataclass
class ValidateLicenseRequest:
    license_key: str = ""
    package_name: str = DEFAULT_PACKAGE
    backend_url: str | None = None
    device_fingerprint: str | None = None


def _service() -> LicenseService:
    return LicenseService(LicenseRepository(get_backend().repository))


def _admin_guard(admin_token: str) -> dict[str, object] | None:
    expected = os.getenv("TTRL_ADMIN_TOKEN", "").strip()
    if not expected:
        return fail(
            "ADMIN_AUTH_NOT_CONFIGURED",
            errors=["Set TTRL_ADMIN_TOKEN in the backend environment before admin license actions."],
        )
    if admin_token != expected:
        return fail("ADMIN_AUTH_FAILED", errors=["Admin token is missing or invalid."])
    return None


def _status_payload(license_id: str, status: LicenseStatus, request: AdminTokenRequest) -> dict[str, object]:
    guarded = _admin_guard(request.admin_token)
    if guarded:
        return guarded
    record = _service().set_status(license_id, status)
    if record is None:
        return fail("LICENSE_NOT_FOUND", errors=[f"No license exists for id {license_id}."])
    return ok(record, message=f"License status set to {status.value}.")


@router.post("/admin/licenses/generate")
def generate_license(request: GenerateLicenseRequest = GenerateLicenseRequest()) -> dict[str, object]:
    guarded = _admin_guard(request.admin_token)
    if guarded:
        return guarded
    try:
        license_type = LicenseType(request.license_type)
    except ValueError:
        return fail("INVALID_LICENSE_TYPE", errors=[request.license_type])
    if not request.client_name.strip():
        return fail("CLIENT_NAME_REQUIRED", errors=["client_name is required."])
    result = _service().generate(
        license_type=license_type,
        client_name=request.client_name.strip(),
        client_email=request.client_email.strip(),
        notes=request.notes.strip(),
        expiry_date=request.expiry_date,
        device_limit=max(1, request.device_limit),
        allowed_app_package=request.allowed_app_package or DEFAULT_PACKAGE,
        backend_url_binding=request.backend_url_binding,
        device_fingerprint_binding=request.device_fingerprint_binding,
    )
    return ok(
        {
            "license_key": result.full_license_key,
            "redacted_license_key": key_generator.redact_license_key(result.full_license_key),
            "record": _service().redacted_record(asdict(result.record)),
            "notice": "Full TTRL license key is returned only once at creation.",
        },
        message="TTRL app license generated.",
    )


@router.get("/admin/licenses")
def list_licenses(admin_token: str = "") -> dict[str, object]:
    guarded = _admin_guard(admin_token)
    if guarded:
        return guarded
    records = [_service().redacted_record(item) for item in _service().repository.list()]
    return ok(records, message="License records loaded without full keys.")


@router.get("/admin/licenses/{license_id}")
def get_license(license_id: str, admin_token: str = "") -> dict[str, object]:
    guarded = _admin_guard(admin_token)
    if guarded:
        return guarded
    record = _service().repository.get_by_id(license_id)
    if record is None:
        return fail("LICENSE_NOT_FOUND", errors=[license_id])
    return ok(_service().redacted_record(record), message="License record loaded without full key.")


@router.post("/admin/licenses/{license_id}/disable")
def disable_license(license_id: str, request: AdminTokenRequest = AdminTokenRequest()) -> dict[str, object]:
    return _status_payload(license_id, LicenseStatus.DISABLED, request)


@router.post("/admin/licenses/{license_id}/revoke")
def revoke_license(license_id: str, request: AdminTokenRequest = AdminTokenRequest()) -> dict[str, object]:
    return _status_payload(license_id, LicenseStatus.REVOKED, request)


@router.post("/admin/licenses/{license_id}/suspend")
def suspend_license(license_id: str, request: AdminTokenRequest = AdminTokenRequest()) -> dict[str, object]:
    return _status_payload(license_id, LicenseStatus.SUSPENDED, request)


@router.post("/admin/licenses/{license_id}/activate")
def activate_license(license_id: str, request: AdminTokenRequest = AdminTokenRequest()) -> dict[str, object]:
    return _status_payload(license_id, LicenseStatus.ACTIVE, request)


@router.post("/license/validate")
def validate_license(request: ValidateLicenseRequest = ValidateLicenseRequest()) -> dict[str, object]:
    result = _service().validate(
        license_key=request.license_key,
        package_name=request.package_name,
        backend_url=request.backend_url,
        device_fingerprint=request.device_fingerprint,
    )
    return ok(asdict(result), message="License validation completed.")
