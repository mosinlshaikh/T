import csv
from dataclasses import dataclass
from pathlib import Path

from modes.scoring import alpha_score, z_score

@dataclass
class BacktestTrade:
    asset: str
    entry_price: float
    exit_price: float
    side: str
    pnl: float
    return_pct: float
    alpha: float
    z: float

@dataclass
class BacktestResult:
    trades: list[BacktestTrade]
    starting_balance: float
    ending_balance: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    net_pnl: float

def apply_costs(entry: float, exit: float, fee_bps: float, slippage_bps: float, side: str) -> tuple[float, float]:
    cost = (fee_bps + slippage_bps) / 10000
    if side.upper() == "LONG":
        return entry * (1 + cost), exit * (1 - cost)
    return entry * (1 - cost), exit * (1 + cost)

def run_backtest(
    csv_path: str,
    starting_balance: float = 10000.0,
    alpha_threshold: float = 65.0,
    z_threshold: float = 2.0,
    hold_bars: int = 2,
    risk_pct: float = 1.0,
    fee_bps: float = 5.0,
    slippage_bps: float = 3.0,
) -> BacktestResult:
    rows = list(csv.DictReader(Path(csv_path).open("r", encoding="utf-8")))
    volumes: list[float] = []
    balance = starting_balance
    equity_peak = starting_balance
    max_drawdown = 0.0
    trades: list[BacktestTrade] = []

    i = 0
    while i < len(rows):
        row = rows[i]
        price = float(row["price"])
        volume = float(row["volume"])
        z = z_score(volume, volumes)
        alpha = alpha_score(
            z=z,
            oi_score=float(row.get("oi_score", 50)),
            sentiment_score=float(row.get("sentiment_score", 50)),
            structure_score=float(row.get("structure_score", 50)),
            whale_score=float(row.get("whale_score", 0)),
            liquidation_score=float(row.get("liquidation_score", 0)),
        )

        if alpha >= alpha_threshold and z >= z_threshold and i + hold_bars < len(rows):
            exit_price = float(rows[i + hold_bars]["price"])
            adj_entry, adj_exit = apply_costs(price, exit_price, fee_bps, slippage_bps, "LONG")
            risk_amount = balance * (risk_pct / 100)
            quantity = risk_amount / max(adj_entry * 0.01, 1e-9)
            pnl = (adj_exit - adj_entry) * quantity
            balance += pnl
            return_pct = pnl / max(starting_balance, 1e-9) * 100

            trades.append(BacktestTrade(
                asset=row["asset"],
                entry_price=round(adj_entry, 4),
                exit_price=round(adj_exit, 4),
                side="LONG",
                pnl=round(pnl, 2),
                return_pct=round(return_pct, 4),
                alpha=alpha,
                z=round(z, 4),
            ))

            equity_peak = max(equity_peak, balance)
            dd = (equity_peak - balance) / equity_peak * 100
            max_drawdown = max(max_drawdown, dd)
            i += hold_bars

        volumes.append(volume)
        if len(volumes) > 50:
            volumes.pop(0)
        i += 1

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    gross_profit = sum(t.pnl for t in wins)
    gross_loss = abs(sum(t.pnl for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss else float("inf") if gross_profit else 0.0

    return BacktestResult(
        trades=trades,
        starting_balance=round(starting_balance, 2),
        ending_balance=round(balance, 2),
        max_drawdown_pct=round(max_drawdown, 2),
        win_rate_pct=round((len(wins) / len(trades) * 100), 2) if trades else 0.0,
        profit_factor=round(profit_factor, 2) if profit_factor != float("inf") else float("inf"),
        net_pnl=round(balance - starting_balance, 2),
    )
