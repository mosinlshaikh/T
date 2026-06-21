from __future__ import annotations

import csv
from dataclasses import dataclass, field
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
class BacktestConfig:
    csv_path: str = ""
    starting_balance: float = 10000.0
    alpha_threshold: float = 65.0
    z_threshold: float = 2.0
    hold_bars: int = 2
    risk_pct: float = 1.0
    fee_bps: float = 5.0
    slippage_bps: float = 2.0
    side: str = "LONG"


@dataclass
class BacktestDiagnostics:
    data_rows: int = 0
    evaluated_bars: int = 0
    warmup_bars: int = 0
    qualified_signals: int = 0
    max_position_size: float = 0.0
    average_position_size: float = 0.0
    max_exposure_pct: float = 0.0


@dataclass
class BacktestResult:
    trades: list[BacktestTrade]
    starting_balance: float
    ending_balance: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    net_pnl: float
    total_trades: int
    average_win: float
    average_loss: float
    best_trade_pnl: float
    worst_trade_pnl: float
    average_return_pct: float
    equity_curve: list[float]
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    expectancy: float = 0.0
    payoff_ratio: float = 0.0
    config: BacktestConfig = field(default_factory=BacktestConfig)
    diagnostics: BacktestDiagnostics = field(default_factory=BacktestDiagnostics)


def validate_backtest_config(config: BacktestConfig) -> None:
    if config.starting_balance <= 0:
        raise ValueError("starting_balance must be greater than 0")
    if config.hold_bars < 1:
        raise ValueError("hold_bars must be at least 1")
    if not 0 < config.risk_pct <= 100:
        raise ValueError("risk_pct must be greater than 0 and less than or equal to 100")
    if config.fee_bps < 0:
        raise ValueError("fee_bps cannot be negative")
    if config.slippage_bps < 0:
        raise ValueError("slippage_bps cannot be negative")
    if config.alpha_threshold < 0:
        raise ValueError("alpha_threshold cannot be negative")
    if config.z_threshold < 0:
        raise ValueError("z_threshold cannot be negative")


def apply_costs(
    entry: float,
    exit: float,
    fee_bps: float,
    slippage_bps: float,
    side: str,
) -> tuple[float, float]:
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
    slippage_bps: float = 2.0,
) -> BacktestResult:
    config = BacktestConfig(
        csv_path=csv_path,
        starting_balance=starting_balance,
        alpha_threshold=alpha_threshold,
        z_threshold=z_threshold,
        hold_bars=hold_bars,
        risk_pct=risk_pct,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
    )
    validate_backtest_config(config)

    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Backtest CSV not found: {csv_path}")

    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    trades: list[BacktestTrade] = []
    volume_history: list[float] = []
    balance = starting_balance
    equity_peak = starting_balance
    max_drawdown_pct = 0.0
    equity_curve = [round(balance, 2)]
    evaluated_bars = 0
    warmup_bars = 0
    qualified_signals = 0
    position_sizes: list[float] = []

    for index, row in enumerate(rows):
        if index + hold_bars >= len(rows):
            break

        volume = float(row.get("volume", 0.0))
        history_window = volume_history[-50:]
        volume_history.append(volume)

        if len(history_window) < 3:
            warmup_bars += 1
            continue

        evaluated_bars += 1
        z = z_score(volume, history_window)
        alpha = alpha_score(
            z=z,
            oi_score=float(row.get("oi_score", 50.0)),
            sentiment_score=float(row.get("sentiment_score", 50.0)),
            structure_score=float(row.get("structure_score", 50.0)),
            whale_score=float(row.get("whale_score", 0.0)),
            liquidation_score=float(row.get("liquidation_score", 0.0)),
        )

        if alpha < alpha_threshold or z < z_threshold:
            continue

        qualified_signals += 1
        entry = float(row.get("price", row.get("entry_price", 0.0)))
        exit_row = rows[index + hold_bars]
        exit_price = float(exit_row.get("price", exit_row.get("exit_price", entry)))

        adj_entry, adj_exit = apply_costs(
            entry=entry,
            exit=exit_price,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            side="LONG",
        )

        position_size = balance * (risk_pct / 100)
        position_sizes.append(position_size)
        units = position_size / max(adj_entry, 1e-9)
        pnl = (adj_exit - adj_entry) * units
        balance += pnl
        equity_curve.append(round(balance, 2))

        return_pct = pnl / max(starting_balance, 1e-9) * 100

        trades.append(
            BacktestTrade(
                asset=row.get("asset", "UNKNOWN"),
                entry_price=round(adj_entry, 4),
                exit_price=round(adj_exit, 4),
                side="LONG",
                pnl=round(pnl, 2),
                return_pct=round(return_pct, 4),
                alpha=round(alpha, 4),
                z=round(z, 4),
            )
        )

        equity_peak = max(equity_peak, balance)
        drawdown_pct = (equity_peak - balance) / max(equity_peak, 1e-9) * 100
        max_drawdown_pct = max(max_drawdown_pct, drawdown_pct)

    wins = [trade for trade in trades if trade.pnl > 0]
    losses = [trade for trade in trades if trade.pnl <= 0]

    gross_profit = sum(trade.pnl for trade in wins)
    gross_loss = abs(sum(trade.pnl for trade in losses))

    if gross_loss:
        profit_factor = gross_profit / gross_loss
    elif gross_profit:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    total_trades = len(trades)
    average_win = round(gross_profit / len(wins), 2) if wins else 0.0
    average_loss = round(sum(trade.pnl for trade in losses) / len(losses), 2) if losses else 0.0
    best_trade_pnl = round(max((trade.pnl for trade in trades), default=0.0), 2)
    worst_trade_pnl = round(min((trade.pnl for trade in trades), default=0.0), 2)
    expectancy = (
        round(sum(trade.pnl for trade in trades) / total_trades, 2) if total_trades else 0.0
    )
    payoff_ratio = (
        round(average_win / abs(average_loss), 4) if average_win and average_loss else 0.0
    )
    average_return_pct = (
        round(sum(trade.return_pct for trade in trades) / total_trades, 4) if total_trades else 0.0
    )

    win_rate_pct = round(len(wins) / total_trades * 100, 2) if total_trades else 0.0
    net_pnl = round(balance - starting_balance, 2)

    return BacktestResult(
        trades=trades,
        starting_balance=round(starting_balance, 2),
        ending_balance=round(balance, 2),
        max_drawdown_pct=round(max_drawdown_pct, 2),
        win_rate_pct=win_rate_pct,
        profit_factor=round(profit_factor, 4) if profit_factor != float("inf") else profit_factor,
        net_pnl=net_pnl,
        total_trades=total_trades,
        average_win=average_win,
        average_loss=average_loss,
        best_trade_pnl=best_trade_pnl,
        worst_trade_pnl=worst_trade_pnl,
        average_return_pct=average_return_pct,
        equity_curve=equity_curve,
        gross_profit=round(gross_profit, 2),
        gross_loss=round(gross_loss, 2),
        expectancy=expectancy,
        payoff_ratio=payoff_ratio,
        config=config,
        diagnostics=BacktestDiagnostics(
            data_rows=len(rows),
            evaluated_bars=evaluated_bars,
            warmup_bars=warmup_bars,
            qualified_signals=qualified_signals,
            max_position_size=round(max(position_sizes, default=0.0), 2),
            average_position_size=(
                round(sum(position_sizes) / len(position_sizes), 2) if position_sizes else 0.0
            ),
            max_exposure_pct=round(risk_pct, 2) if position_sizes else 0.0,
        ),
    )
