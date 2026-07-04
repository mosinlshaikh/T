from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    status: str
    reasons: list[str]


def evaluate_risk(
    trade_size_pct: float,
    daily_loss_pct: float,
    consecutive_losses: int,
    open_trades: int,
    stop_loss: float | None,
    take_profit: float | None,
) -> RiskResult:
    reasons: list[str] = []
    if trade_size_pct > 5:
        reasons.append("Max active risk 5% exceeded.")
    if trade_size_pct >= 85:
        reasons.append("No all-in trade allowed.")
    if daily_loss_pct > 3:
        reasons.append("Daily loss limit exceeded.")
    if consecutive_losses >= 3:
        reasons.append("Consecutive loss cooldown required.")
    if open_trades >= 3:
        reasons.append("Max open trades reached.")
    if stop_loss is None:
        reasons.append("Stop-loss required.")
    if take_profit is None:
        reasons.append("Take-profit required.")
    return RiskResult("SAFE" if not reasons else "UNSAFE", reasons)
