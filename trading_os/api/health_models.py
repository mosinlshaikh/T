from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from trading_os.portfolio.state import WalletSnapshot


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ApiResponse:
    success: bool
    message: str
    data: object | None = None
    timestamp: str = field(default_factory=utc_now)
    request_id: str = field(default_factory=lambda: str(uuid4()))
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BotStatusModel:
    state: str
    healthy: bool
    failure_state: str
    heartbeat_count: int


@dataclass(frozen=True)
class ConfigStatusModel:
    runtime_mode: str
    live_trading_enabled: bool
    withdrawals_supported: bool
    config_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VaultStatusModel:
    provider: str
    api_key_available: bool
    api_secret_available: bool
    credential_pair_available: bool


@dataclass(frozen=True)
class BinanceReadinessStatusModel:
    status: str
    ready: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PortfolioSummaryModel:
    wallet: dict[str, object]
    open_positions: int
    closed_positions: int
    exposure: float
    available_capital: float
    daily_pnl: float
    drawdown_pct: float

    @classmethod
    def from_wallet(cls, wallet: WalletSnapshot, **kwargs: object) -> "PortfolioSummaryModel":
        return cls(wallet=asdict(wallet), **kwargs)


@dataclass(frozen=True)
class HealthSnapshotModel:
    bot_status: BotStatusModel
    config_status: ConfigStatusModel
    vault_status: VaultStatusModel
    binance_readiness_status: BinanceReadinessStatusModel
    portfolio_summary: PortfolioSummaryModel
    latest_decisions: list[dict[str, object]] = field(default_factory=list)
    latest_audit_events: list[dict[str, object]] = field(default_factory=list)
    shutdown_status: dict[str, object] = field(default_factory=dict)
