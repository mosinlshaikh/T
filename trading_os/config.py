from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
from typing import Mapping


class RuntimeMode(str, Enum):
    PAPER = "paper"
    SANDBOX = "sandbox"
    LIVE_DISABLED = "live_disabled"


def _env_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_env_file(path: str = ".env") -> dict[str, str]:
    """Load simple KEY=VALUE pairs from a local env file without exposing secrets."""

    loaded: dict[str, str] = {}
    if not os.path.exists(path):
        return loaded
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded[key] = value
    return loaded


@dataclass(frozen=True)
class TradingOSConfig:
    """Runtime configuration with safe defaults.

    No API keys are read here. Secrets must be handled by the key vault design,
    and live execution remains disabled until a future audited phase.
    """

    runtime_mode: RuntimeMode = RuntimeMode.PAPER
    default_symbol: str = "BTCUSDT"
    enable_live_trading: bool = False
    manual_live_unlock: bool = False
    allow_withdraw_permissions: bool = False
    require_verified_evidence: bool = True
    database_url: str = "sqlite:///data/trading_os.sqlite3"
    audit_log_path: str = "data/audit/trading_os_audit.jsonl"
    binance_api_key_available: bool = False
    binance_api_secret_available: bool = False

    @classmethod
    def from_env(cls) -> "TradingOSConfig":
        load_env_file()
        mode = (
            os.getenv("TRADING_MODE")
            or os.getenv("BINANCE_MODE")
            or os.getenv("T_TRADING_MODE")
            or RuntimeMode.PAPER.value
        ).lower()
        if mode == "live":
            mode = RuntimeMode.LIVE_DISABLED.value
        if mode not in {item.value for item in RuntimeMode}:
            mode = RuntimeMode.PAPER.value
        return cls(
            runtime_mode=RuntimeMode(mode),
            default_symbol=os.getenv("T_DEFAULT_SYMBOL", "BTCUSDT").upper(),
            enable_live_trading=False,
            manual_live_unlock=_env_bool(os.getenv("MANUAL_LIVE_UNLOCK"), False),
            allow_withdraw_permissions=False,
            require_verified_evidence=True,
            database_url=os.getenv("T_DATABASE_URL", "sqlite:///data/trading_os.sqlite3"),
            audit_log_path=os.getenv("T_AUDIT_LOG_PATH", "data/audit/trading_os_audit.jsonl"),
            binance_api_key_available=bool(os.getenv("BINANCE_API_KEY")),
            binance_api_secret_available=bool(os.getenv("BINANCE_API_SECRET")),
        )

    def assert_safe(self) -> None:
        if self.enable_live_trading:
            raise RuntimeError("Live trading is disabled in this backend foundation.")
        if self.manual_live_unlock:
            raise RuntimeError("Manual live unlock is disabled in this backend foundation.")
        if self.allow_withdraw_permissions:
            raise RuntimeError("Withdraw permissions are not supported.")

    def validate(self) -> "ConfigValidationResult":
        errors: list[str] = []
        warnings: list[str] = []
        if self.enable_live_trading:
            errors.append("LIVE_TRADING_ENABLED must remain false.")
        if self.manual_live_unlock:
            errors.append("MANUAL_LIVE_UNLOCK must remain false.")
        if self.allow_withdraw_permissions:
            errors.append("BINANCE_WITHDRAWALS_SUPPORTED must remain false.")
        if self.runtime_mode not in {
            RuntimeMode.PAPER,
            RuntimeMode.SANDBOX,
            RuntimeMode.LIVE_DISABLED,
        }:
            errors.append("Unsupported runtime mode.")
        if not self.default_symbol:
            errors.append("Default symbol is required.")
        if self.runtime_mode == RuntimeMode.LIVE_DISABLED:
            warnings.append("Live mode was requested but is blocked by design.")
        return ConfigValidationResult(valid=not errors, errors=errors, warnings=warnings)

    def redacted(self) -> dict[str, object]:
        return redact_config(
            {
                "TRADING_MODE": self.runtime_mode.value,
                "LIVE_TRADING_ENABLED": self.enable_live_trading,
                "MANUAL_LIVE_UNLOCK": self.manual_live_unlock,
                "BINANCE_WITHDRAWALS_SUPPORTED": self.allow_withdraw_permissions,
                "DEFAULT_SYMBOL": self.default_symbol,
                "DATABASE_URL": self.database_url,
                "AUDIT_LOG_PATH": self.audit_log_path,
                "BINANCE_API_KEY": "<available>" if self.binance_api_key_available else "",
                "BINANCE_API_SECRET": "<available>" if self.binance_api_secret_available else "",
            }
        )

    def health_report(self) -> dict[str, object]:
        validation = self.validate()
        return {
            "runtime_mode": self.runtime_mode.value,
            "live_trading_enabled": self.enable_live_trading,
            "manual_live_unlock": self.manual_live_unlock,
            "withdrawals_supported": self.allow_withdraw_permissions,
            "config_valid": validation.valid,
            "errors": validation.errors,
            "warnings": validation.warnings,
            "secrets": {
                "binance_api_key_available": self.binance_api_key_available,
                "binance_api_secret_available": self.binance_api_secret_available,
            },
        }


@dataclass(frozen=True)
class ConfigValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


def redact_config(values: Mapping[str, object]) -> dict[str, object]:
    secret_markers = {"KEY", "SECRET", "TOKEN", "PASSWORD"}
    redacted: dict[str, object] = {}
    for key, value in values.items():
        if any(marker in key.upper() for marker in secret_markers):
            redacted[key] = "<redacted>" if value else ""
        else:
            redacted[key] = value
    return redacted
