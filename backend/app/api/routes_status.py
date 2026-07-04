from __future__ import annotations

from backend.app.config import CONFIG


def status() -> dict[str, object]:
    return {
        "route": "/api/status",
        "mode": CONFIG.trading_mode.value,
        "live_trading_enabled": False,
    }
