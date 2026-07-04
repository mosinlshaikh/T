from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candle:
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: str


def candle_signal(candles: list[Candle]) -> dict[str, object]:
    if not candles:
        return {"signal": "SKIP", "missing_data": ["candles"], "evidence": []}
    latest = candles[-1]
    direction = (
        "BUY" if latest.close > latest.open else "SELL" if latest.close < latest.open else "HOLD"
    )
    return {"signal": direction, "evidence": [latest.__dict__], "missing_data": []}
