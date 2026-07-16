from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.candle_intelligence import CandleIntelligenceEngine
from trading_os.intelligence.order_book_intelligence import OrderBookIntelligenceEngine
from trading_os.market.candle_engine import Candle
from trading_os.market.order_book_engine import OrderBookLevel, OrderBookSnapshot
from trading_os.market.timeframes import Timeframe
from trading_os.strategies.registry import StrategyName, StrategyRegistry


def candle(close: float, index: int) -> Candle:
    return Candle(
        symbol="BTCUSDT",
        timeframe=Timeframe.FIVE_MINUTES,
        open=close - 1,
        high=close + 0.25,
        low=close - 1.25,
        close=close,
        volume=100,
        start_time_ms=index * 300_000,
        end_time_ms=(index + 1) * 300_000,
    )


def test_candle_trend_only_can_emit_buy_when_evidence_is_sufficient() -> None:
    signal = CandleIntelligenceEngine().analyze(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [candle(100, 1), candle(101, 2), candle(102, 3)],
    )

    assert signal.direction == DecisionAction.BUY
    assert signal.confidence >= 0.5
    assert signal.evidence


def test_candle_rejection_overrides_trend_direction() -> None:
    candles = [
        candle(100, 1),
        candle(101, 2),
        Candle(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            open=101,
            high=120,
            low=100,
            close=102,
            volume=100,
            start_time_ms=900_000,
            end_time_ms=1_200_000,
        ),
    ]

    signal = CandleIntelligenceEngine().analyze("BTCUSDT", Timeframe.FIVE_MINUTES, candles)

    assert signal.direction == DecisionAction.HOLD


def test_order_book_imbalance_can_emit_buy_without_wall() -> None:
    snapshot = OrderBookSnapshot(
        symbol="BTCUSDT",
        bids=[
            OrderBookLevel(price=100.0, quantity=18.0),
            OrderBookLevel(price=99.9, quantity=16.0),
            OrderBookLevel(price=99.8, quantity=15.0),
        ],
        asks=[
            OrderBookLevel(price=100.01, quantity=8.0),
            OrderBookLevel(price=100.02, quantity=7.0),
            OrderBookLevel(price=100.03, quantity=6.0),
        ],
    )

    signal = OrderBookIntelligenceEngine().analyze("BTCUSDT", Timeframe.FIVE_MINUTES, snapshot)

    assert signal.direction == DecisionAction.BUY
    assert signal.evidence


def test_order_book_spread_risk_blocks_imbalance_direction() -> None:
    snapshot = OrderBookSnapshot(
        symbol="BTCUSDT",
        bids=[
            OrderBookLevel(price=100.0, quantity=18.0),
            OrderBookLevel(price=99.9, quantity=16.0),
        ],
        asks=[
            OrderBookLevel(price=101.0, quantity=2.0),
            OrderBookLevel(price=101.1, quantity=2.0),
        ],
    )

    signal = OrderBookIntelligenceEngine().analyze("BTCUSDT", Timeframe.FIVE_MINUTES, snapshot)

    assert signal.direction == DecisionAction.HOLD
    assert signal.risk_score > 0


def test_default_strategy_registry_preserves_directional_market_evidence() -> None:
    candle_signal = CandleIntelligenceEngine().analyze(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [candle(100, 1), candle(101, 2), candle(102, 3)],
    )
    order_book_signal = OrderBookIntelligenceEngine().analyze(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        OrderBookSnapshot(
            symbol="BTCUSDT",
            bids=[
                OrderBookLevel(price=100.0, quantity=18.0),
                OrderBookLevel(price=99.9, quantity=16.0),
            ],
            asks=[
                OrderBookLevel(price=100.01, quantity=6.0),
                OrderBookLevel(price=100.02, quantity=5.0),
            ],
        ),
    )

    strategy_signals = StrategyRegistry.with_default_placeholders().evaluate_all(
        "BTCUSDT",
        candle_signal.evidence + order_book_signal.evidence,
    )
    directions = {signal.source: signal.direction for signal in strategy_signals}

    assert directions[StrategyName.CANDLE_STRUCTURE_STRATEGY.value] == DecisionAction.BUY
    assert directions[StrategyName.ORDER_BOOK_LIQUIDITY_STRATEGY.value] == DecisionAction.BUY


def test_candle_strategy_ignores_market_structure_candle_evidence_for_confidence() -> None:
    candle_signal = CandleIntelligenceEngine().analyze(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [candle(100, 1), candle(101, 2), candle(102, 3)],
    )
    market_structure_candle_evidence = EvidenceItem(
        evidence_type=EvidenceType.CANDLE,
        source="market_structure",
        summary="neutral market structure evidence",
        confidence=0.45,
        payload={"range_vs_trend": "range"},
    )

    strategy_signals = StrategyRegistry.with_default_placeholders().evaluate_all(
        "BTCUSDT",
        candle_signal.evidence + [market_structure_candle_evidence],
    )
    directions = {signal.source: signal.direction for signal in strategy_signals}
    confidences = {signal.source: signal.confidence for signal in strategy_signals}

    assert directions[StrategyName.CANDLE_STRUCTURE_STRATEGY.value] == DecisionAction.BUY
    assert confidences[StrategyName.CANDLE_STRUCTURE_STRATEGY.value] >= 0.5
