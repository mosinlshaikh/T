from trading_os.intelligence.candle_study import CandleStudyEngine
from trading_os.market.candle_engine import Candle
from trading_os.market.live_public_data import BinancePublicMarketDataClient
from trading_os.market.timeframes import Timeframe, binance_interval_for, normalize_timeframe


def test_timeframe_aliases_and_synthetic_10m() -> None:
    assert normalize_timeframe("24h") == Timeframe.ONE_DAY
    assert normalize_timeframe("1month") == Timeframe.ONE_MONTH
    assert normalize_timeframe("10m") == Timeframe.TEN_MINUTES
    assert binance_interval_for("10m") == Timeframe.FIVE_MINUTES


def test_aggregate_5m_to_10m() -> None:
    candles = [
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 100, 103, 99, 102, 10, 1, 2),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 102, 104, 101, 103, 20, 3, 4),
    ]
    aggregated = BinancePublicMarketDataClient._aggregate_5m_to_10m(candles, "BTCUSDT")
    assert len(aggregated) == 1
    assert aggregated[0].timeframe == Timeframe.TEN_MINUTES
    assert aggregated[0].open == 100
    assert aggregated[0].high == 104
    assert aggregated[0].low == 99
    assert aggregated[0].close == 103
    assert aggregated[0].volume == 30


def test_candle_study_missing_data_is_safe() -> None:
    study = CandleStudyEngine().study("BTCUSDT", "5m", [])
    assert study.missing_data == ["candles"]
    assert study.confidence_score == 0.0
    assert "No Data = No Trade" in study.move_reason


def test_candle_study_explains_move_with_evidence() -> None:
    candles = [
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 100, 101, 99, 100.5, 10, 1, 2),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 100.5, 102, 100, 101.5, 11, 3, 4),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 101.5, 103, 101, 102.5, 12, 5, 6),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 102.5, 104, 102, 103.5, 13, 7, 8),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 103.5, 106, 103, 105.5, 25, 9, 10),
    ]
    study = CandleStudyEngine().study("BTCUSDT", "5m", candles)
    assert study.missing_data == []
    assert study.latest_close == 105.5
    assert study.confidence_score > 0
    assert study.evidence
    assert study.learning_notes
