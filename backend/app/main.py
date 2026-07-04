from __future__ import annotations

from backend.app.config import CONFIG
from backend.app.api.routes_status import status


def create_app() -> dict[str, object]:
    CONFIG.assert_safe()
    return {
        "name": "T AI Binance Trading OS Backend",
        "mode": CONFIG.trading_mode.value,
        "live_trading_enabled": CONFIG.live_trading_enabled,
        "status": status(),
    }


app = create_app()
