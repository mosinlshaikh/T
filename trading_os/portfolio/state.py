from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class WalletSnapshot:
    usdt_balance: float
    reserved_capital: float
    realized_pnl: float
    unrealized_pnl: float
    timestamp: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class Position:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reserved_capital: float
    position_id: str = field(default_factory=lambda: str(uuid4()))
    opened_at: str = field(default_factory=utc_now)
    closed_at: str | None = None
    realized_pnl: float = 0.0
    status: str = "OPEN"


@dataclass
class PortfolioStateManager:
    starting_balance: float = 10000.0
    reserve_capital_pct: float = 10.0
    usdt_balance: float = field(init=False)
    reserved_capital: float = 0.0
    realized_pnl: float = 0.0
    open_positions: dict[str, Position] = field(default_factory=dict)
    closed_positions: list[Position] = field(default_factory=list)
    daily_realized: dict[str, float] = field(default_factory=dict)
    equity_peak: float = field(init=False)

    def __post_init__(self) -> None:
        self.usdt_balance = self.starting_balance
        self.equity_peak = self.starting_balance

    def reserve_for_position(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Reserved amount must be positive.")
        if amount > self.available_capital():
            raise ValueError("Reserved amount exceeds available capital.")
        self.reserved_capital += amount

    def release_reserve(self, amount: float) -> None:
        self.reserved_capital = max(self.reserved_capital - amount, 0.0)

    def add_position(self, position: Position) -> None:
        self.reserve_for_position(position.reserved_capital)
        self.open_positions[position.position_id] = position

    def close_position(self, position_id: str, exit_price: float, fee: float = 0.0) -> Position:
        position = self.open_positions.pop(position_id)
        pnl = self._pnl(position, exit_price) - fee
        closed = replace(
            position,
            closed_at=utc_now(),
            realized_pnl=round(pnl, 8),
            status="CLOSED",
        )
        self.release_reserve(position.reserved_capital)
        self.realized_pnl += closed.realized_pnl
        self.usdt_balance += closed.realized_pnl
        self.closed_positions.append(closed)
        today = date.today().isoformat()
        self.daily_realized[today] = self.daily_realized.get(today, 0.0) + closed.realized_pnl
        self.equity_peak = max(self.equity_peak, self.equity())
        return closed

    def partial_exit(
        self,
        position_id: str,
        exit_price: float,
        exit_quantity: float,
        fee: float = 0.0,
    ) -> Position:
        position = self.open_positions[position_id]
        if exit_quantity <= 0 or exit_quantity >= position.quantity:
            raise ValueError(
                "Partial exit quantity must be greater than 0 and below position size."
            )

        ratio = exit_quantity / position.quantity
        pnl = self._pnl(position, exit_price, quantity=exit_quantity) - fee
        remaining = replace(
            position,
            quantity=round(position.quantity - exit_quantity, 8),
            reserved_capital=round(position.reserved_capital * (1 - ratio), 8),
        )
        released = position.reserved_capital - remaining.reserved_capital
        self.open_positions[position_id] = remaining
        self.release_reserve(released)
        self.realized_pnl += pnl
        self.usdt_balance += pnl
        today = date.today().isoformat()
        self.daily_realized[today] = self.daily_realized.get(today, 0.0) + pnl
        return remaining

    def wallet_snapshot(self, mark_prices: dict[str, float] | None = None) -> WalletSnapshot:
        return WalletSnapshot(
            usdt_balance=round(self.usdt_balance, 8),
            reserved_capital=round(self.reserved_capital, 8),
            realized_pnl=round(self.realized_pnl, 8),
            unrealized_pnl=round(self.unrealized_pnl(mark_prices or {}), 8),
        )

    def exposure(self) -> float:
        return round(sum(position.reserved_capital for position in self.open_positions.values()), 8)

    def available_capital(self) -> float:
        reserve_lock = self.usdt_balance * (self.reserve_capital_pct / 100)
        return round(max(self.usdt_balance - reserve_lock - self.reserved_capital, 0.0), 8)

    def daily_pnl(self, day: str | None = None) -> float:
        return round(self.daily_realized.get(day or date.today().isoformat(), 0.0), 8)

    def drawdown_pct(self, mark_prices: dict[str, float] | None = None) -> float:
        equity = self.equity(mark_prices or {})
        if self.equity_peak <= 0:
            return 0.0
        return round(max((self.equity_peak - equity) / self.equity_peak * 100, 0.0), 4)

    def unrealized_pnl(self, mark_prices: dict[str, float]) -> float:
        return sum(
            self._pnl(position, mark_prices[position.symbol])
            for position in self.open_positions.values()
            if position.symbol in mark_prices
        )

    def equity(self, mark_prices: dict[str, float] | None = None) -> float:
        return self.usdt_balance + self.unrealized_pnl(mark_prices or {})

    @staticmethod
    def _pnl(position: Position, exit_price: float, quantity: float | None = None) -> float:
        qty = quantity if quantity is not None else position.quantity
        direction = 1 if position.side.upper() == "BUY" else -1
        return (exit_price - position.entry_price) * qty * direction
