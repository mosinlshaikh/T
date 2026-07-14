from __future__ import annotations

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.derivatives.risk import DerivativesRiskGuard

router = APIRouter(prefix="/derivatives", tags=["derivatives"])


@router.get("/readiness")
def derivatives_readiness() -> dict[str, object]:
    backend = get_backend()
    guard = DerivativesRiskGuard()
    return ok(
        guard.readiness(live_trading_enabled=backend.config.enable_live_trading),
        "F&O derivatives readiness loaded. Live derivatives execution remains blocked.",
    )


@router.get("/risk-estimate")
def derivatives_risk_estimate(
    symbol: str = "BTCUSDT",
    instrument: str = "FUTURES",
    notional_usdt: float = 100.0,
    leverage: float = 2.0,
    adverse_move_pct: float = 1.0,
) -> dict[str, object]:
    guard = DerivativesRiskGuard()
    return ok(
        guard.estimate(
            symbol=symbol,
            instrument=instrument,
            notional_usdt=notional_usdt,
            leverage=leverage,
            adverse_move_pct=adverse_move_pct,
        ),
        "Paper-only F&O risk estimate loaded.",
    )
