from __future__ import annotations

from enum import Enum


class Timeframe(str, Enum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    TEN_MINUTES = "10m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    ONE_DAY = "1d"
    ONE_MONTH = "1M"


SUPPORTED_TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe.ONE_MINUTE,
    Timeframe.FIVE_MINUTES,
    Timeframe.TEN_MINUTES,
    Timeframe.FIFTEEN_MINUTES,
    Timeframe.ONE_HOUR,
    Timeframe.FOUR_HOURS,
    Timeframe.EIGHT_HOURS,
    Timeframe.ONE_DAY,
    Timeframe.ONE_MONTH,
)

TIMEFRAME_ALIASES: dict[str, Timeframe] = {
    "24h": Timeframe.ONE_DAY,
    "24hr": Timeframe.ONE_DAY,
    "1day": Timeframe.ONE_DAY,
    "1d": Timeframe.ONE_DAY,
    "1mo": Timeframe.ONE_MONTH,
    "1month": Timeframe.ONE_MONTH,
    "1M": Timeframe.ONE_MONTH,
}

BINANCE_NATIVE_TIMEFRAMES: set[Timeframe] = {
    Timeframe.ONE_MINUTE,
    Timeframe.FIVE_MINUTES,
    Timeframe.FIFTEEN_MINUTES,
    Timeframe.ONE_HOUR,
    Timeframe.FOUR_HOURS,
    Timeframe.EIGHT_HOURS,
    Timeframe.ONE_DAY,
    Timeframe.ONE_MONTH,
}


def normalize_timeframe(value: str | Timeframe) -> Timeframe:
    if isinstance(value, Timeframe):
        return value
    clean = str(value).strip()
    if clean in TIMEFRAME_ALIASES:
        return TIMEFRAME_ALIASES[clean]
    return Timeframe(clean)


def binance_interval_for(timeframe: str | Timeframe) -> Timeframe:
    tf = normalize_timeframe(timeframe)
    if tf == Timeframe.TEN_MINUTES:
        return Timeframe.FIVE_MINUTES
    return tf


def is_synthetic_timeframe(timeframe: str | Timeframe) -> bool:
    return normalize_timeframe(timeframe) not in BINANCE_NATIVE_TIMEFRAMES
