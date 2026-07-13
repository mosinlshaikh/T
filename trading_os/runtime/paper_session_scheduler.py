from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PaperSessionScheduler:
    """Session-level scheduler for repeated public-market paper scans."""

    backend: Any
    min_interval_seconds: int = 60
    running: bool = False
    session_id: str = ""
    started_at: str = ""
    stopped_at: str = ""
    symbols: list[str] = field(default_factory=list)
    timeframe: str = "5m"
    interval_seconds: int = 300
    trade_notional_usdt: float = 50.0
    scan_count: int = 0
    last_scan: dict[str, Any] | None = None
    last_error: str = ""
    _thread: Thread | None = field(default=None, init=False, repr=False)
    _stop: Event = field(default_factory=Event, init=False, repr=False)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def start(
        self,
        symbols: list[str] | None = None,
        timeframe: str = "5m",
        interval_seconds: int = 300,
        trade_notional_usdt: float = 50.0,
    ) -> dict[str, Any]:
        if self.backend.config.enable_live_trading:
            raise RuntimeError("Paper session refuses to run when live trading is enabled.")
        if self.backend.kill_switch.active:
            raise RuntimeError("Emergency kill switch is active.")

        with self._lock:
            if self.running:
                return self.status()
            self.session_id = str(uuid4())
            self.started_at = utc_now()
            self.stopped_at = ""
            self.symbols = [item.strip().upper() for item in (symbols or []) if item.strip()]
            self.timeframe = timeframe
            self.interval_seconds = max(int(interval_seconds), self.min_interval_seconds)
            self.trade_notional_usdt = min(max(float(trade_notional_usdt), 10.0), 250.0)
            self.scan_count = 0
            self.last_scan = None
            self.last_error = ""
            self._stop.clear()
            self.running = True
            self._thread = Thread(target=self._loop, daemon=True)
            self._thread.start()

        self.backend.audit_logger.log(
            "paper_session_started",
            {
                "session_id": self.session_id,
                "symbols": self.symbols,
                "timeframe": self.timeframe,
                "interval_seconds": self.interval_seconds,
                "live_trading_enabled": False,
                "public_data_only": True,
            },
        )
        return self.status()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        with self._lock:
            self.running = False
            self.stopped_at = utc_now()
        self.backend.audit_logger.log(
            "paper_session_stopped",
            {"session_id": self.session_id, "stopped_at": self.stopped_at},
        )
        return self.status()

    def status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "session_id": self.session_id,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "symbols": self.symbols,
            "timeframe": self.timeframe,
            "interval_seconds": self.interval_seconds,
            "trade_notional_usdt": self.trade_notional_usdt,
            "scan_count": self.scan_count,
            "last_scan": self.last_scan,
            "last_error": self.last_error,
            "live_trading_enabled": False,
            "public_data_only": True,
        }

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                payload = self.backend.paper_auto_trader.scan_once(
                    symbols=self.symbols or None,
                    timeframe=self.timeframe,
                    trade_notional_usdt=self.trade_notional_usdt,
                )
                with self._lock:
                    self.last_scan = payload
                    self.scan_count += 1
                    self.last_error = ""
                self.backend.audit_logger.log(
                    "paper_session_scan",
                    {
                        "session_id": self.session_id,
                        "scan_count": self.scan_count,
                        "best_candidate": payload.get("best_candidate"),
                        "errors": payload.get("errors", []),
                        "live_trading_enabled": False,
                    },
                )
            except Exception as exc:
                with self._lock:
                    self.last_error = f"{exc.__class__.__name__}: paper session scan skipped safely"
                self.backend.audit_logger.log_skipped_trade(
                    {
                        "session_id": self.session_id,
                        "reason": "Paper session scan skipped safely.",
                        "error": exc.__class__.__name__,
                    }
                )
            if self._stop.wait(self.interval_seconds):
                break
        with self._lock:
            self.running = False
            if not self.stopped_at:
                self.stopped_at = utc_now()
