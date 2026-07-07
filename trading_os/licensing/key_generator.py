from __future__ import annotations

import secrets
import string

ALPHABET = string.ascii_uppercase + string.digits


def generate_license_key() -> str:
    groups = ["".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(4)]
    return "TTRL-" + "-".join(groups)


def is_valid_key_format(license_key: str) -> bool:
    parts = license_key.strip().upper().split("-")
    return (
        len(parts) == 5
        and parts[0] == "TTRL"
        and all(len(part) == 4 and part.isalnum() for part in parts[1:])
    )


def redact_license_key(license_key: str) -> str:
    normalized = license_key.strip().upper()
    if not is_valid_key_format(normalized):
        return "TTRL-****-****-****-****"
    return f"{normalized[:9]}-****-****-{normalized[-4:]}"
