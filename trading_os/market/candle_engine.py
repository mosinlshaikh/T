from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.market.market_data_engine import MarketTick
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class Candle:
    symbol: str
    timeframe: Timeframe
    open: float
    high: float
    low: float
    close: float
    volume: float
    start_time_ms: int
    end_time_ms: int


@dataclass
class CandleEngine:
    candles: list[Candle] = field(default_factory=list)

    def build_single_tick_candle(
        self,
        tick: MarketTick,
        timeframe: str | Timeframe = Timeframe.ONE_MINUTE,
        interval_ms: int = 60_000,
    ) -> Candle:
        candle = Candle(
            symbol=tick.symbol.upper(),
            timeframe=normalize_timeframe(timeframe),
            open=tick.price,
            high=tick.price,
            low=tick.price,
            close=tick.price,
            volume=tick.volume,
            start_time_ms=tick.event_time_ms,
            end_time_ms=tick.event_time_ms + interval_ms,
        )
        self.candles.append(candle)
        return candle

    def collect(self, candles: list[Candle]) -> None:
        self.candles.extend(candles)

    def by_timeframe(self, symbol: str, timeframe: str | Timeframe) -> list[Candle]:
        tf = normalize_timeframe(timeframe)
        return [
            candle
            for candle in self.candles
            if candle.symbol.upper() == symbol.upper() and candle.timeframe == tf
        ]
