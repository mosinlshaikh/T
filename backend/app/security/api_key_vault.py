from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CredentialAvailability:
    api_key_available: bool = False
    api_secret_available: bool = False
    withdrawals_supported: bool = False


class ApiKeyVault:
    def availability(self) -> CredentialAvailability:
        return CredentialAvailability()

    def store_secret(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Raw secret storage is not implemented in repository code.")
