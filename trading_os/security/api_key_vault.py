from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import os


class SecretProviderType(str, Enum):
    ENV_PROVIDER = "ENV_PROVIDER"
    LOCAL_VAULT_PROVIDER = "LOCAL_VAULT_PROVIDER"
    CLOUD_SECRET_PROVIDER = "CLOUD_SECRET_PROVIDER"


@dataclass(frozen=True)
class CredentialAvailability:
    provider: SecretProviderType
    api_key_available: bool
    api_secret_available: bool

    @property
    def complete(self) -> bool:
        return self.api_key_available and self.api_secret_available


@dataclass(frozen=True)
class ApiCredentialMetadata:
    label: str
    exchange: str
    can_read: bool = True
    can_trade: bool = False
    can_withdraw: bool = False


@dataclass(frozen=True)
class PermissionExpectation:
    reading: bool = True
    spot_trading: bool = False
    withdrawals: bool = False


class SecretProvider:
    provider_type: SecretProviderType

    def availability(self) -> CredentialAvailability:
        raise NotImplementedError


@dataclass
class EnvSecretProvider(SecretProvider):
    provider_type: SecretProviderType = SecretProviderType.ENV_PROVIDER

    def availability(self) -> CredentialAvailability:
        return CredentialAvailability(
            provider=self.provider_type,
            api_key_available=bool(os.getenv("BINANCE_API_KEY")),
            api_secret_available=bool(os.getenv("BINANCE_API_SECRET")),
        )


@dataclass
class LocalVaultSecretProvider(SecretProvider):
    provider_type: SecretProviderType = SecretProviderType.LOCAL_VAULT_PROVIDER

    def availability(self) -> CredentialAvailability:
        return CredentialAvailability(self.provider_type, False, False)


@dataclass
class CloudSecretProvider(SecretProvider):
    provider_type: SecretProviderType = SecretProviderType.CLOUD_SECRET_PROVIDER

    def availability(self) -> CredentialAvailability:
        return CredentialAvailability(self.provider_type, False, False)


@dataclass
class ApiKeyVaultDesign:
    """API key vault design placeholder.

    This class never stores raw API keys. Future implementations should use
    OS keychain, cloud KMS, or encrypted local storage outside git.
    """

    provider: SecretProvider = field(default_factory=EnvSecretProvider)
    expectation: PermissionExpectation = field(default_factory=PermissionExpectation)

    def credential_availability(self) -> CredentialAvailability:
        return self.provider.availability()

    def health_report(self) -> dict[str, object]:
        availability = self.credential_availability()
        return {
            "provider": availability.provider.value,
            "api_key_available": availability.api_key_available,
            "api_secret_available": availability.api_secret_available,
            "credential_pair_available": availability.complete,
            "permission_expectation": {
                "reading": self.expectation.reading,
                "spot_trading": self.expectation.spot_trading,
                "withdrawals": self.expectation.withdrawals,
            },
        }

    def validate_metadata(self, metadata: ApiCredentialMetadata) -> None:
        if metadata.can_withdraw:
            raise RuntimeError("Withdraw permission support is forbidden.")
        if not metadata.can_read:
            raise RuntimeError("Read permission is required for market/account verification.")

    def store_secret(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("Secret storage must be implemented outside repository code.")
