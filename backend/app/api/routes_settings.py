from __future__ import annotations


def settings() -> dict[str, object]:
    return {"route": "/api/settings", "live_trading_enabled": False, "withdrawals_supported": False}
