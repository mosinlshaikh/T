from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import VerifiedDecision
from trading_os.execution.intent import ExecutionIntent
from trading_os.intelligence.news_risk_intelligence import NewsItem
from trading_os.intelligence.whale_intelligence_v1 import WhaleTrade
from trading_os.market.candle_engine import Candle
from trading_os.market.order_book_engine import OrderBookSnapshot
from trading_os.market.timeframes import Timeframe
from trading_os.paper.simulator import PaperFill
from trading_os.trade.lifecycle import TradeContext


@dataclass(frozen=True)
class PipelineInput:
    symbol: str
    timeframe: Timeframe
    market_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    account_balance: float
    current_exposure: float = 0.0
    daily_realized_loss: float = 0.0
    consecutive_losses: int = 0
    minutes_since_last_loss: int | None = None
    candles: list[Candle] | None = None
    order_book: OrderBookSnapshot | None = None
    whale_trades: list[WhaleTrade] | None = None
    news_items: list[NewsItem] | None = None


@dataclass(frozen=True)
class PipelineResult:
    symbol: str
    timeframe: Timeframe
    decision: VerifiedDecision
    trade_context: TradeContext | None
    execution_intent: ExecutionIntent | None
    paper_fill: PaperFill | None
    status: str
    reason: str
    stage_results: list[dict[str, object]]
