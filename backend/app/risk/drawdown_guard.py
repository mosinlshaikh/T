from __future__ import annotations


def drawdown_status(drawdown_pct: float, max_drawdown_pct: float = 10.0) -> str:
    return "BLOCK" if drawdown_pct >= max_drawdown_pct else "OK"
