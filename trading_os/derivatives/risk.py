from __future__ import annotations

from dataclasses import asdict, dataclass

from trading_os.derivatives.models import (
    DerivativesInstrument,
    DerivativesReadiness,
    DerivativesRiskEstimate,
)


@dataclass
class DerivativesRiskGuard:
    """F&O/Futures research guard.

    This intentionally does not place futures/options orders. It only explains
    paper risk and keeps derivatives live execution blocked.
    """

    max_demo_leverage: float = 3.0
    max_demo_notional_usdt: float = 250.0

    def readiness(self, live_trading_enabled: bool = False) -> dict[str, object]:
        blocked = [
            "Futures live execution is not implemented.",
            "Options live execution is not implemented.",
            "Leverage can amplify losses and liquidation risk.",
            "Margin/futures permissions are not supported in this build.",
            "Derivatives are research/paper-only until a separate audited phase.",
        ]
        report = DerivativesReadiness(
            live_trading_enabled=False,
            blocked_reasons=blocked,
            allowed_features=[
                "F&O education",
                "paper-only leverage risk estimate",
                "derivatives readiness checklist",
                "spot strategy cross-check",
            ],
            warnings=[
                "No guaranteed profit.",
                "Paper results do not prove real-money performance.",
                "Live trading remains disabled even if live_trading_enabled input is true.",
            ]
            + (["Requested live mode is ignored and blocked."] if live_trading_enabled else []),
        )
        return asdict(report)

    def estimate(
        self,
        symbol: str = "BTCUSDT",
        instrument: str = "FUTURES",
        notional_usdt: float = 100.0,
        leverage: float = 2.0,
        adverse_move_pct: float = 1.0,
    ) -> dict[str, object]:
        safe_notional = min(max(float(notional_usdt), 10.0), self.max_demo_notional_usdt)
        safe_leverage = min(max(float(leverage), 1.0), self.max_demo_leverage)
        safe_adverse = min(max(float(adverse_move_pct), 0.1), 25.0)
        margin = safe_notional / safe_leverage
        estimated_loss = safe_notional * (safe_adverse / 100.0)
        liquidation_warning = (
            "High liquidation risk: adverse move is large relative to demo leverage."
            if safe_adverse * safe_leverage >= 8.0
            else "Liquidation risk exists; use paper-only analysis."
        )
        estimate = DerivativesRiskEstimate(
            instrument=DerivativesInstrument(instrument.upper()),
            symbol=symbol.upper(),
            notional_usdt=round(safe_notional, 8),
            leverage=round(safe_leverage, 2),
            margin_estimate_usdt=round(margin, 8),
            adverse_move_pct=round(safe_adverse, 4),
            estimated_loss_usdt=round(estimated_loss, 8),
            liquidation_warning=liquidation_warning,
            safety_notes=[
                "This is a paper/research estimate only.",
                "No futures/options order is sent.",
                "No margin account or leverage permission is used.",
                "Use spot paper evidence before considering any future derivatives phase.",
            ],
        )
        return asdict(estimate)
