from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from time import sleep
from typing import Any
from uuid import uuid4

from trading_os.market.live_public_data import BinancePublicMarketDataClient


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PaperAutoTraderResult:
    run_id: str
    symbol: str
    timeframe: str
    status: str
    action: str
    confidence: float
    reason: str
    paper_fill_id: str = ""
    timestamp: str = field(default_factory=utc_now)


@dataclass
class PaperAutoTrader:
    """Public-market paper loop.

    This component is deliberately paper-only. It reads unauthenticated public
    market data, uses the existing evidence-first decision pipeline, and never
    sends private Binance requests or real orders.
    """

    backend: Any
    default_symbols: tuple[str, ...] = ("BTCUSDT",)
    default_timeframe: str = "5m"
    default_trade_notional_usdt: float = 50.0
    min_interval_seconds: int = 30
    running: bool = False
    last_result: PaperAutoTraderResult | None = None
    last_error: str = ""
    run_count: int = 0
    _thread: Thread | None = field(default=None, init=False, repr=False)
    _stop: Event = field(default_factory=Event, init=False, repr=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def run_once(
        self,
        symbol: str = "BTCUSDT",
        timeframe: str = "5m",
        trade_notional_usdt: float = 50.0,
    ) -> PaperAutoTraderResult:
        if self.backend.config.enable_live_trading:
            raise RuntimeError("Paper auto trader refuses to run when live trading is enabled.")
        if self.backend.kill_switch.active:
            raise RuntimeError("Emergency kill switch is active.")

        safe_notional = min(max(float(trade_notional_usdt), 10.0), 250.0)
        client = BinancePublicMarketDataClient()
        bundle = client.fetch_bundle(symbol=symbol, timeframe=timeframe)

        self.backend.market_data.ingest_rest_snapshot(bundle.snapshot)
        self.backend.candle_engine.collect(bundle.candles)
        self.backend.order_book_engine.update_snapshot(bundle.order_book)
        self.backend.audit_logger.log_market_snapshot(
            {
                "symbol": bundle.symbol,
                "timeframe": bundle.timeframe.value,
                "price": bundle.snapshot.price,
                "volume_24h": bundle.snapshot.volume_24h,
                "source": bundle.snapshot.source,
                "candles": len(bundle.candles),
                "order_book_bids": len(bundle.order_book.bids),
                "order_book_asks": len(bundle.order_book.asks),
                "whale_trades": len(bundle.whale_trades),
                "news_items": len(bundle.news_items),
                "public_data_only": True,
                "auto_paper_loop": True,
            }
        )

        pipeline_input = client.build_pipeline_input(
            bundle=bundle,
            account_balance=self.backend.portfolio.usdt_balance,
            current_exposure=self.backend.portfolio.exposure(),
            trade_notional_usdt=safe_notional,
        )
        result = self.backend.decision_to_trade_pipeline.run(pipeline_input, bundle.evidence)
        auto_result = PaperAutoTraderResult(
            run_id=str(uuid4()),
            symbol=result.symbol,
            timeframe=result.timeframe.value,
            status=result.status,
            action=result.decision.action.value,
            confidence=result.decision.confidence,
            reason=result.reason,
            paper_fill_id=result.paper_fill.fill_id if result.paper_fill else "",
        )
        self.last_result = auto_result
        self.last_error = ""
        self.run_count += 1
        self.backend.audit_logger.log(
            "paper_auto_trader_tick",
            {
                **asdict(auto_result),
                "live_trading_enabled": False,
                "public_data_only": True,
            },
        )
        return auto_result

    def start(
        self,
        symbols: list[str] | None = None,
        timeframe: str = "5m",
        interval_seconds: int = 60,
        trade_notional_usdt: float = 50.0,
    ) -> dict[str, Any]:
        with self._lock:
            if self.running:
                return self.status()
            safe_symbols = [item.upper() for item in (symbols or list(self.default_symbols))][:5]
            safe_interval = max(int(interval_seconds), self.min_interval_seconds)
            self._stop.clear()
            self.running = True
            self._thread = Thread(
                target=self._loop,
                args=(safe_symbols, timeframe, safe_interval, trade_notional_usdt),
                daemon=True,
            )
            self._thread.start()
        self.backend.audit_logger.log(
            "paper_auto_trader_started",
            {
                "symbols": safe_symbols,
                "timeframe": timeframe,
                "interval_seconds": safe_interval,
                "live_trading_enabled": False,
            },
        )
        return self.status()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        with self._lock:
            self.running = False
        self.backend.audit_logger.log("paper_auto_trader_stopped", {"stopped_at": utc_now()})
        return self.status()

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "run_count": self.run_count,
            "last_error": self.last_error,
            "last_result": asdict(self.last_result) if self.last_result else None,
            "live_trading_enabled": False,
            "public_data_only": True,
        }

    def _loop(
        self,
        symbols: list[str],
        timeframe: str,
        interval_seconds: int,
        trade_notional_usdt: float,
    ) -> None:
        while not self._stop.is_set():
            for symbol in symbols:
                if self._stop.is_set():
                    break
                try:
                    self.run_once(symbol, timeframe, trade_notional_usdt)
                except Exception as exc:
                    self.last_error = f"{exc.__class__.__name__}: paper tick skipped safely"
                    self.backend.audit_logger.log_skipped_trade(
                        {
                            "symbol": symbol,
                            "reason": "Paper auto trader tick skipped safely.",
                            "error": exc.__class__.__name__,
                        }
                    )
            sleep(interval_seconds)
        with self._lock:
            self.running = False
