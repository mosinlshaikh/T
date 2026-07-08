from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Event, Lock, Thread
from time import sleep
from typing import Any
from uuid import uuid4

from trading_os.market.live_public_data import BinancePublicMarketDataClient

DEFAULT_WATCHLIST_PATH = "config/watchlist.json"


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
    default_symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")
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

    def scan_once(
        self,
        symbols: list[str] | None = None,
        timeframe: str = "5m",
        trade_notional_usdt: float = 50.0,
    ) -> dict[str, Any]:
        watchlist = load_watchlist_config()
        configured_symbols = watchlist.get("symbols", list(self.default_symbols))
        max_symbols = int(watchlist.get("max_symbols_per_scan", 5) or 5)
        safe_symbols = normalize_watchlist(symbols or configured_symbols, max_symbols=max_symbols)
        results: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        for symbol in safe_symbols:
            try:
                result = self.run_once(symbol, timeframe, trade_notional_usdt)
                results.append(enrich_scan_result(asdict(result)))
            except Exception as exc:
                errors.append(
                    {
                        "symbol": symbol,
                        "error": exc.__class__.__name__,
                        "reason": "Paper scanner skipped symbol safely.",
                    }
                )
                self.backend.audit_logger.log_skipped_trade(
                    {
                        "symbol": symbol,
                        "reason": "Paper scanner skipped symbol safely.",
                        "error": exc.__class__.__name__,
                    }
                )
        ranked = sorted(
            results,
            key=lambda item: (
                1 if item.get("action") in {"BUY", "SELL"} else 0,
                float(item.get("confidence", 0.0) or 0.0),
            ),
            reverse=True,
        )
        payload = {
            "symbols": safe_symbols,
            "timeframe": timeframe,
            "results": ranked,
            "errors": errors,
            "best_candidate": ranked[0] if ranked else None,
            "live_trading_enabled": False,
            "public_data_only": True,
        }
        self.backend.audit_logger.log("paper_auto_trader_scan", payload)
        return payload

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
            watchlist = load_watchlist_config()
            configured_symbols = watchlist.get("symbols", list(self.default_symbols))
            max_symbols = int(watchlist.get("max_symbols_per_scan", 5) or 5)
            safe_symbols = normalize_watchlist(
                symbols or configured_symbols, max_symbols=max_symbols
            )
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


def load_watchlist_config(path: str = DEFAULT_WATCHLIST_PATH) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {
            "symbols": ["BTCUSDT", "ETHUSDT"],
            "default_timeframe": "5m",
            "max_symbols_per_scan": 5,
            "paper_trade_notional_usdt": 50.0,
        }
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"symbols": ["BTCUSDT", "ETHUSDT"], "max_symbols_per_scan": 5}
    return payload if isinstance(payload, dict) else {"symbols": ["BTCUSDT", "ETHUSDT"]}


def normalize_watchlist(symbols: list[str] | tuple[str, ...], max_symbols: int = 5) -> list[str]:
    normalized: list[str] = []
    for symbol in symbols:
        clean = str(symbol).strip().upper()
        if not clean or not clean.endswith("USDT") or clean in normalized:
            continue
        normalized.append(clean)
        if len(normalized) >= max(1, max_symbols):
            break
    return normalized


def confidence_band(confidence: float) -> str:
    if confidence >= 0.7:
        return "HIGH"
    if confidence >= 0.45:
        return "MEDIUM"
    if confidence > 0:
        return "LOW"
    return "UNKNOWN"


def trade_allowed(action: str, confidence: float, status: str) -> bool:
    return action in {"BUY", "SELL"} and confidence >= 0.7 and status == "PAPER_OPEN"


def why_not_traded(action: str, confidence: float, status: str, reason: str) -> str:
    if trade_allowed(action, confidence, status):
        return ""
    if action in {"HOLD", "SKIP"}:
        return reason or f"Action is {action}; paper trade not opened."
    if confidence < 0.7:
        return "Confidence below paper trade threshold."
    return reason or "Paper trade was not opened by risk or verification policy."


def enrich_scan_result(result: dict[str, Any]) -> dict[str, Any]:
    confidence = float(result.get("confidence", 0.0) or 0.0)
    action = str(result.get("action", "SKIP"))
    status = str(result.get("status", "SKIP"))
    reason = str(result.get("reason", ""))
    return {
        **result,
        "confidence_band": confidence_band(confidence),
        "trade_allowed": trade_allowed(action, confidence, status),
        "why_not_traded": why_not_traded(action, confidence, status, reason),
        "reason_summary": reason[:180],
    }
