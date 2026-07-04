from __future__ import annotations

from backend.app.market.candle_engine import Candle


def structure_summary(candles: list[Candle]) -> dict[str, object]:
    if len(candles) < 3:
        return {"structure": "unknown", "missing_data": ["market_structure_history"]}
    highs = [candle.high for candle in candles[-3:]]
    lows = [candle.low for candle in candles[-3:]]
    if highs == sorted(highs) and lows == sorted(lows):
        return {"structure": "uptrend", "missing_data": []}
    if highs == sorted(highs, reverse=True) and lows == sorted(lows, reverse=True):
        return {"structure": "downtrend", "missing_data": []}
    return {"structure": "range", "missing_data": []}
