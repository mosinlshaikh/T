from __future__ import annotations


def start() -> dict[str, object]:
    return {"route": "/api/start", "accepted": True, "mode": "paper"}


def stop() -> dict[str, object]:
    return {"route": "/api/stop", "accepted": True}


def kill_switch() -> dict[str, object]:
    return {"route": "/api/kill-switch", "state": "EMERGENCY_STOP"}


def risk() -> dict[str, object]:
    return {"route": "/api/risk", "reserve_capital_pct": 10, "max_active_risk_pct": 5}
