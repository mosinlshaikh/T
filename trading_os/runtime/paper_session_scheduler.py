from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
from threading import Event, Lock, Thread
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_symbols(name: str) -> list[str]:
    value = os.getenv(name, "")
    return [item.strip().upper() for item in value.split(",") if item.strip()]


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
    settings_key: str = "paper_session"

    def _desired_settings(self) -> dict[str, Any]:
        repository = getattr(self.backend, "repository", None)
        if repository is None:
            return {}
        try:
            settings = repository.get_settings(self.settings_key)
        except Exception:
            return {}
        return settings if isinstance(settings, dict) else {}

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
            self._save_desired_state(enabled=True)

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
        self._save_desired_state(enabled=False)
        self.backend.audit_logger.log(
            "paper_session_stopped",
            {"session_id": self.session_id, "stopped_at": self.stopped_at},
        )
        return self.status()

    def status(self) -> dict[str, Any]:
        desired = self._desired_settings()
        started = _parse_utc(self.started_at)
        now = datetime.now(timezone.utc)
        uptime_seconds = max(int((now - started).total_seconds()), 0) if started else 0
        expected_scans = max(int(uptime_seconds // max(self.interval_seconds, 1)), 0)
        expected_scans_24h = max(int(86_400 // max(self.interval_seconds, 1)), 1)
        health = (
            "RUNNING"
            if self.running and not self.last_error
            else "DEGRADED" if self.running else "STOPPED"
        )
        if self.running and self.scan_count == 0 and uptime_seconds > self.interval_seconds * 2:
            health = "DEGRADED"
        return {
            "running": self.running,
            "session_id": self.session_id,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "uptime_seconds": uptime_seconds,
            "uptime_hours": round(uptime_seconds / 3600, 4),
            "target_window_hours": 24,
            "monitoring_health": health,
            "symbols": self.symbols,
            "timeframe": self.timeframe,
            "interval_seconds": self.interval_seconds,
            "trade_notional_usdt": self.trade_notional_usdt,
            "scan_count": self.scan_count,
            "expected_scan_count": expected_scans,
            "expected_scan_count_24h": expected_scans_24h,
            "scan_progress_24h_pct": round(
                min((self.scan_count / expected_scans_24h) * 100, 100), 2
            ),
            "last_scan": self.last_scan,
            "last_error": self.last_error,
            "auto_resume_enabled": bool(desired.get("enabled")),
            "desired_symbols": desired.get("symbols", []),
            "desired_timeframe": desired.get("timeframe", self.timeframe),
            "desired_interval_seconds": desired.get("interval_seconds", self.interval_seconds),
            "live_trading_enabled": False,
            "public_data_only": True,
        }

    def auto_resume_if_configured(self) -> dict[str, Any]:
        settings = self._desired_settings() or self._env_desired_state()
        if self.running or not settings.get("enabled"):
            return self.status()
        if self.backend.config.enable_live_trading or self.backend.kill_switch.active:
            self.backend.audit_logger.log_skipped_trade(
                {
                    "reason": "Paper session auto-resume blocked by safety state.",
                    "live_trading_enabled": bool(self.backend.config.enable_live_trading),
                    "kill_switch_active": bool(self.backend.kill_switch.active),
                }
            )
            return self.status()
        symbols = settings.get("symbols", [])
        if not isinstance(symbols, list):
            symbols = []
        status = self.start(
            symbols=[str(item).upper() for item in symbols[:25]],
            timeframe=str(settings.get("timeframe", "5m")),
            interval_seconds=int(settings.get("interval_seconds", self.interval_seconds) or 300),
            trade_notional_usdt=float(
                settings.get("trade_notional_usdt", self.trade_notional_usdt) or 50.0
            ),
        )
        self.backend.audit_logger.log(
            "paper_session_auto_resumed",
            {
                "session_id": self.session_id,
                "symbols": self.symbols,
                "timeframe": self.timeframe,
                "interval_seconds": self.interval_seconds,
                "live_trading_enabled": False,
                "public_data_only": True,
            },
        )
        return status

    def _env_desired_state(self) -> dict[str, Any]:
        if not env_flag("T_PAPER_SESSION_ENABLED", default=False):
            return {}
        return {
            "enabled": True,
            "symbols": env_symbols("T_PAPER_SESSION_SYMBOLS")
            or ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
            "timeframe": os.getenv("T_PAPER_SESSION_TIMEFRAME", "5m"),
            "interval_seconds": int(os.getenv("T_PAPER_SESSION_INTERVAL_SECONDS", "300") or 300),
            "trade_notional_usdt": float(
                os.getenv("T_PAPER_SESSION_TRADE_NOTIONAL_USDT", "50") or 50.0
            ),
            "live_trading_enabled": False,
            "public_data_only": True,
            "source": "environment",
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

    def _save_desired_state(self, enabled: bool) -> None:
        repository = getattr(self.backend, "repository", None)
        if repository is None:
            return
        repository.save_settings(
            self.settings_key,
            {
                "enabled": enabled,
                "symbols": self.symbols,
                "timeframe": self.timeframe,
                "interval_seconds": self.interval_seconds,
                "trade_notional_usdt": self.trade_notional_usdt,
                "updated_at": utc_now(),
                "live_trading_enabled": False,
                "public_data_only": True,
            },
        )
