from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from trading_os.config import RuntimeMode, TradingOSConfig
from trading_os.security.api_key_vault import (
    ApiCredentialMetadata,
    ApiKeyVaultDesign,
    CredentialAvailability,
    PermissionExpectation,
)


class ApiReadinessStatus(str, Enum):
    READY_FOR_PAPER = "READY_FOR_PAPER"
    READY_FOR_SANDBOX = "READY_FOR_SANDBOX"
    LIVE_BLOCKED = "LIVE_BLOCKED"
    MISCONFIGURED = "MISCONFIGURED"
    SECRET_MISSING = "SECRET_MISSING"


@dataclass(frozen=True)
class ApiReadinessResult:
    status: ApiReadinessStatus
    ready: bool
    reasons: list[str] = field(default_factory=list)
    metadata_checked: bool = False


@dataclass
class BinanceApiPermissionVerifier:
    expectation: PermissionExpectation = field(default_factory=PermissionExpectation)

    def verify(
        self,
        config: TradingOSConfig,
        vault: ApiKeyVaultDesign,
        metadata: ApiCredentialMetadata | None = None,
    ) -> ApiReadinessResult:
        validation = config.validate()
        if not validation.valid:
            return ApiReadinessResult(
                ApiReadinessStatus.MISCONFIGURED,
                False,
                validation.errors,
                metadata_checked=metadata is not None,
            )

        if config.enable_live_trading:
            return ApiReadinessResult(
                ApiReadinessStatus.LIVE_BLOCKED,
                False,
                ["Live trading is blocked by default."],
                metadata_checked=metadata is not None,
            )

        if metadata is not None:
            metadata_result = self._metadata_result(metadata)
            if metadata_result is not None:
                return metadata_result

        availability = vault.credential_availability()
        if config.runtime_mode == RuntimeMode.SANDBOX and not availability.complete:
            return self._secret_missing(availability, metadata is not None)

        if config.runtime_mode == RuntimeMode.LIVE_DISABLED:
            return ApiReadinessResult(
                ApiReadinessStatus.LIVE_BLOCKED,
                False,
                ["Live mode request is blocked by design."],
                metadata_checked=metadata is not None,
            )

        if config.runtime_mode == RuntimeMode.SANDBOX:
            return ApiReadinessResult(
                ApiReadinessStatus.READY_FOR_SANDBOX,
                True,
                ["Credential pair is available for sandbox readiness checks."],
                metadata_checked=metadata is not None,
            )

        return ApiReadinessResult(
            ApiReadinessStatus.READY_FOR_PAPER,
            True,
            ["Paper mode does not require Binance credentials."],
            metadata_checked=metadata is not None,
        )

    def _metadata_result(self, metadata: ApiCredentialMetadata) -> ApiReadinessResult | None:
        if self.expectation.reading and not metadata.can_read:
            return ApiReadinessResult(
                ApiReadinessStatus.MISCONFIGURED,
                False,
                ["Read permission is required."],
                metadata_checked=True,
            )
        if metadata.can_withdraw or self.expectation.withdrawals:
            return ApiReadinessResult(
                ApiReadinessStatus.MISCONFIGURED,
                False,
                ["Withdraw permission must be disabled."],
                metadata_checked=True,
            )
        return None

    @staticmethod
    def _secret_missing(
        availability: CredentialAvailability, metadata_checked: bool
    ) -> ApiReadinessResult:
        missing: list[str] = []
        if not availability.api_key_available:
            missing.append("BINANCE_API_KEY unavailable")
        if not availability.api_secret_available:
            missing.append("BINANCE_API_SECRET unavailable")
        return ApiReadinessResult(
            ApiReadinessStatus.SECRET_MISSING,
            False,
            missing,
            metadata_checked=metadata_checked,
        )
