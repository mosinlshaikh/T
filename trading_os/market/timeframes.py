from __future__ import annotations

from enum import Enum


class Timeframe(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"


SUPPORTED_TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe.ONE_MINUTE,
    Timeframe.FIVE_MINUTES,
    Timeframe.FIFTEEN_MINUTES,
    Timeframe.ONE_HOUR,
    Timeframe.FOUR_HOURS,
)


def normalize_timeframe(value: str | Timeframe) -> Timeframe:
    if isinstance(value, Timeframe):
        return value
    return Timeframe(value)
