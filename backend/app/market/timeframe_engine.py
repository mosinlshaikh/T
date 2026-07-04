from __future__ import annotations

SUPPORTED_TIMEFRAMES = {"1m", "5m", "15m", "1h", "4h"}


def normalize_timeframe(timeframe: str) -> str:
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError("Unsupported timeframe.")
    return timeframe
