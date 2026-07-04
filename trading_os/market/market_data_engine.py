from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.connectors.rest_api import RestApiConnector, RestApiRequest
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class MarketTick:
    symbol: str
    price: float
    volume: float
    event_time_ms: int
    source: str = "binance_public"


@dataclass(frozen=True)
class RestMarketSnapshot:
    symbol: str
    price: float
    volume_24h: float
    event_time_ms: int
    source: str = "binance_rest_snapshot"


@dataclass(frozen=True)
class CandleDataRequest:
    symbol: str
    timeframe: Timeframe
    limit: int = 500


@dataclass(frozen=True)
class VolumeSpike:
    symbol: str
    timeframe: Timeframe
    current_volume: float
    average_volume: float
    spike_ratio: float
    detected: bool


@dataclass
class MarketDataEngine:
    ticks: list[MarketTick] = field(default_factory=list)
    snapshots: dict[str, RestMarketSnapshot] = field(default_factory=dict)
    rest_api: RestApiConnector = field(default_factory=RestApiConnector)

    def ingest_tick(self, tick: MarketTick) -> None:
        if tick.price <= 0 or tick.volume < 0:
            raise ValueError("Invalid market tick: price must be positive and volume non-negative.")
        self.ticks.append(tick)

    def latest_tick(self, symbol: str) -> MarketTick | None:
        symbol = symbol.upper()
        for tick in reversed(self.ticks):
            if tick.symbol.upper() == symbol:
                return tick
        return None

    def rest_snapshot_request(self, symbol: str) -> RestApiRequest:
        return self.rest_api.build_public_request("/api/v3/ticker/24hr", {"symbol": symbol.upper()})

    def ingest_rest_snapshot(self, snapshot: RestMarketSnapshot) -> None:
        if snapshot.price <= 0 or snapshot.volume_24h < 0:
            raise ValueError("Invalid market snapshot.")
        self.snapshots[snapshot.symbol.upper()] = snapshot

    def candle_request(
        self, symbol: str, timeframe: str | Timeframe, limit: int = 500
    ) -> CandleDataRequest:
        return CandleDataRequest(symbol.upper(), normalize_timeframe(timeframe), limit)


@dataclass
class VolumeSpikeDetector:
    threshold_ratio: float = 2.0

    def detect(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        current_volume: float,
        historical_volumes: list[float],
    ) -> VolumeSpike:
        tf = normalize_timeframe(timeframe)
        if not historical_volumes:
            return VolumeSpike(symbol.upper(), tf, current_volume, 0.0, 0.0, False)
        average = sum(historical_volumes) / len(historical_volumes)
        ratio = current_volume / average if average else 0.0
        return VolumeSpike(
            symbol=symbol.upper(),
            timeframe=tf,
            current_volume=current_volume,
            average_volume=round(average, 8),
            spike_ratio=round(ratio, 4),
            detected=ratio >= self.threshold_ratio,
        )
