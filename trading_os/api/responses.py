from __future__ import annotations

from dataclasses import asdict
from typing import Any

from trading_os.api.framework import jsonable
from trading_os.api.health_models import ApiResponse

SECRET_MARKERS = ("key", "secret", "token", "password", "credential")


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if key_text in {"license_key", "redacted_license_key"}:
                redacted[str(key)] = item
            elif any(marker in key_text for marker in SECRET_MARKERS):
                redacted[str(key)] = "<redacted>" if item else item
            else:
                redacted[str(key)] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def ok(
    data: Any = None,
    message: str = "ok",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    response = ApiResponse(
        success=True,
        message=message,
        data=redact_sensitive(jsonable(data)),
        warnings=warnings or [],
    )
    return asdict(response)


def fail(
    message: str,
    errors: list[str] | None = None,
    data: Any = None,
) -> dict[str, Any]:
    response = ApiResponse(
        success=False,
        message=message,
        data=redact_sensitive(jsonable(data)),
        errors=errors or [],
    )
    return asdict(response)
