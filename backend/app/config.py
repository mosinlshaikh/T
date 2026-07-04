from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os


class TradingMode(str, Enum):
    PAPER = "paper"
    SANDBOX = "sandbox"
    READ_ONLY = "read_only"


@dataclass(frozen=True)
class BackendConfig:
    trading_mode: TradingMode = TradingMode.PAPER
    live_trading_enabled: bool = False
    manual_live_unlock: bool = False
    binance_spot_only: bool = True
    withdrawals_supported: bool = False
    private_key_supported: bool = False
    reserve_capital_pct: float = 10.0
    max_active_risk_pct: float = 5.0
    growth_capital_pct: float = 85.0
    daily_loss_limit_pct: float = 3.0
    consecutive_loss_cooldown_minutes: int = 30
    max_open_trades: int = 3

    @classmethod
    def from_env(cls) -> "BackendConfig":
        mode = os.getenv("TRADING_MODE", TradingMode.PAPER.value).lower()
        if mode not in {item.value for item in TradingMode}:
            mode = TradingMode.PAPER.value
        return cls(
            trading_mode=TradingMode(mode),
            live_trading_enabled=False,
            manual_live_unlock=False,
            withdrawals_supported=False,
            private_key_supported=False,
        )

    def assert_safe(self) -> None:
        if self.live_trading_enabled:
            raise RuntimeError("LIVE_TRADING_ENABLED must remain false in this foundation.")
        if self.manual_live_unlock:
            raise RuntimeError("MANUAL_LIVE_UNLOCK must remain false in this foundation.")
        if self.withdrawals_supported or self.private_key_supported:
            raise RuntimeError("Withdrawals and private key support are forbidden.")


CONFIG = BackendConfig.from_env()
