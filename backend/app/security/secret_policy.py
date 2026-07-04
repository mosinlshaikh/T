from __future__ import annotations

FORBIDDEN_SECRET_STORAGE = {"api_key", "api_secret", "private_key", "withdraw_key"}


def redact(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: (
            "<redacted>"
            if any(marker in key.lower() for marker in FORBIDDEN_SECRET_STORAGE)
            else value
        )
        for key, value in payload.items()
    }
