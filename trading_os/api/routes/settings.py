from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok

router = APIRouter(prefix="/settings", tags=["settings"])


@dataclass
class RiskSettings:
    reserve_capital_pct: float = 10.0
    max_risk_exposure_pct: float = 5.0
    max_trade_size_usdt: float = 500.0
    daily_loss_limit_pct: float = 3.0
    consecutive_loss_limit: int = 3
    cooldown_minutes_after_loss: int = 30
    stop_loss_required: bool = True
    take_profit_required: bool = True


@dataclass
class StrategySettings:
    enabled_strategies: list[str] = field(default_factory=list)
    evidence_required: bool = True
    zero_hallucination_required: bool = True


@dataclass
class NotificationSettings:
    telegram_enabled: bool = False
    whatsapp_enabled: bool = False
    email_enabled: bool = False


_risk_settings = RiskSettings()
_strategy_settings = StrategySettings()
_notification_settings = NotificationSettings()


@router.get("/risk")
def get_risk() -> dict[str, object]:
    persisted = get_backend().repository.get_settings("risk")
    return ok(persisted or _risk_settings, "Risk settings loaded.")


@router.put("/risk")
def put_risk(settings: RiskSettings) -> dict[str, object]:
    warnings: list[str] = []
    settings.reserve_capital_pct = max(min(settings.reserve_capital_pct, 50.0), 10.0)
    settings.max_risk_exposure_pct = max(min(settings.max_risk_exposure_pct, 5.0), 0.1)
    settings.max_trade_size_usdt = max(min(settings.max_trade_size_usdt, 10_000.0), 1.0)
    settings.daily_loss_limit_pct = max(min(settings.daily_loss_limit_pct, 10.0), 0.1)
    settings.consecutive_loss_limit = max(min(settings.consecutive_loss_limit, 10), 1)
    settings.cooldown_minutes_after_loss = max(settings.cooldown_minutes_after_loss, 1)
    settings.stop_loss_required = True
    settings.take_profit_required = True
    warnings.append("Stop-loss and take-profit remain required.")
    global _risk_settings
    _risk_settings = settings
    get_backend().repository.save_settings("risk", settings.__dict__)
    return ok(_risk_settings, "Risk settings updated with safe limits.", warnings=warnings)


@router.get("/strategy")
def get_strategy() -> dict[str, object]:
    backend = get_backend()
    data = {
        "registered_strategies": [item.value for item in backend.strategies.strategies.keys()],
        "settings": backend.repository.get_settings("strategy") or _strategy_settings,
    }
    return ok(data, "Strategy settings loaded.")


@router.put("/strategy")
def put_strategy(settings: StrategySettings) -> dict[str, object]:
    settings.evidence_required = True
    settings.zero_hallucination_required = True
    global _strategy_settings
    _strategy_settings = settings
    get_backend().repository.save_settings("strategy", settings.__dict__)
    return ok(_strategy_settings, "Strategy settings updated.")


@router.get("/security")
def get_security() -> dict[str, object]:
    backend = get_backend()
    return ok(
        {
            "live_trading_enabled": False,
            "withdrawals_supported": False,
            "vault_status": backend.api_vault.health_report(),
            "api_key_submission_endpoint": "not_available",
        },
        "Security settings loaded.",
    )


@router.get("/notifications")
def get_notifications() -> dict[str, object]:
    persisted = get_backend().repository.get_settings("notifications")
    return ok(persisted or _notification_settings, "Notification settings loaded.")


@router.put("/notifications")
def put_notifications(settings: NotificationSettings) -> dict[str, object]:
    global _notification_settings
    _notification_settings = settings
    get_backend().repository.save_settings("notifications", settings.__dict__)
    return ok(_notification_settings, "Notification settings updated.")
