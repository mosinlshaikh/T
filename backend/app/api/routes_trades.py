from __future__ import annotations


def trades() -> dict[str, object]:
    return {"route": "/api/trades", "trades": [], "mode": "paper"}


def positions() -> dict[str, object]:
    return {"route": "/api/positions", "positions": [], "mode": "paper"}
