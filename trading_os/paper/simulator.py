from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from trading_os.audit.trade_journal import JournalEntry, TradeJournal
from trading_os.db.repository import TradingOSRepository
from trading_os.execution.intent import ExecutionIntent, OrderIntentType
from trading_os.portfolio.state import PortfolioStateManager, Position


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PaperFill:
    intent_id: str
    position_id: str
    symbol: str
    side: str
    quantity: float
    fill_price: float
    fee: float
    event_type: str
    fill_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=utc_now)


@dataclass
class PaperTradingSimulator:
    portfolio: PortfolioStateManager = field(default_factory=PortfolioStateManager)
    journal: TradeJournal = field(default_factory=TradeJournal)
    repository: TradingOSRepository | None = None
    fee_rate: float = 0.001
    fills: list[PaperFill] = field(default_factory=list)

    def open_trade(self, intent: ExecutionIntent, fill_price: float) -> PaperFill:
        self._assert_paper_intent(intent)
        if intent.intent_type not in {OrderIntentType.MARKET_BUY, OrderIntentType.LIMIT_BUY}:
            raise ValueError("Open trade supports buy intents in spot paper mode.")

        notional = intent.quantity * fill_price
        fee = self._fee(notional)
        position = Position(
            symbol=intent.symbol.upper(),
            side="BUY",
            quantity=intent.quantity,
            entry_price=fill_price,
            stop_loss=intent.stop_loss,
            take_profit=intent.take_profit,
            reserved_capital=notional + fee,
        )
        self.portfolio.add_position(position)
        fill = self._record_fill(intent, position.position_id, fill_price, fee, "PAPER_OPEN")
        self._record_journal(position.symbol, "PAPER_OPEN", intent.reason)
        return fill

    def close_trade(
        self, position_id: str, intent: ExecutionIntent, fill_price: float
    ) -> PaperFill:
        self._assert_paper_intent(intent)
        position = self.portfolio.open_positions[position_id]
        fee = self._fee(position.quantity * fill_price)
        closed = self.portfolio.close_position(position_id, fill_price, fee)
        fill = self._record_fill(intent, closed.position_id, fill_price, fee, "PAPER_CLOSED")
        self._record_journal(closed.symbol, "PAPER_CLOSED", intent.reason)
        return fill

    def partial_exit(
        self,
        position_id: str,
        intent: ExecutionIntent,
        fill_price: float,
        exit_quantity: float,
    ) -> PaperFill:
        self._assert_paper_intent(intent)
        fee = self._fee(exit_quantity * fill_price)
        remaining = self.portfolio.partial_exit(position_id, fill_price, exit_quantity, fee)
        fill = self._record_fill(
            intent, remaining.position_id, fill_price, fee, "PAPER_PARTIAL_EXIT"
        )
        self._record_journal(remaining.symbol, "PAPER_PARTIAL_EXIT", intent.reason)
        return fill

    def simulate_stop_loss_hit(self, position_id: str, intent: ExecutionIntent) -> PaperFill:
        position = self.portfolio.open_positions[position_id]
        return self.close_trade(position_id, intent, position.stop_loss)

    def simulate_take_profit_hit(self, position_id: str, intent: ExecutionIntent) -> PaperFill:
        position = self.portfolio.open_positions[position_id]
        return self.close_trade(position_id, intent, position.take_profit)

    def _record_fill(
        self,
        intent: ExecutionIntent,
        position_id: str,
        fill_price: float,
        fee: float,
        event_type: str,
    ) -> PaperFill:
        fill = PaperFill(
            intent_id=intent.intent_id,
            position_id=position_id,
            symbol=intent.symbol.upper(),
            side=intent.side,
            quantity=intent.quantity,
            fill_price=fill_price,
            fee=round(fee, 8),
            event_type=event_type,
        )
        self.fills.append(fill)
        return fill

    def _record_journal(self, symbol: str, action: str, reason: str) -> None:
        entry = self.journal.record(
            JournalEntry(symbol=symbol, action=action, mode="paper", reason=reason)
        )
        if self.repository is not None:
            self.repository.save_trade_journal_entry(entry)

    def _fee(self, notional: float) -> float:
        return notional * self.fee_rate

    @staticmethod
    def _assert_paper_intent(intent: ExecutionIntent) -> None:
        if intent.live_enabled:
            raise RuntimeError("Paper simulator refuses live-enabled intents.")
