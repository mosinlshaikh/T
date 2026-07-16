from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.signal_combiner import MultiFactorSignalCombiner
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.timeframes import Timeframe


def evidence(name: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_type=EvidenceType.CANDLE,
        source=name,
        summary=f"{name} evidence",
        confidence=0.8,
    )


def intel(
    name: str,
    direction: DecisionAction,
    confidence: float = 0.8,
    risk_score: float = 0.0,
    missing_data: list[str] | None = None,
) -> IntelligenceSignal:
    return IntelligenceSignal(
        name=name,
        symbol="BTCUSDT",
        timeframe=Timeframe.FIVE_MINUTES,
        direction=direction,
        confidence=confidence,
        evidence=[evidence(name)] if not missing_data else [],
        reason=f"{name} test signal",
        risk_score=risk_score,
        missing_data=missing_data or [],
    )


def test_combiner_can_buy_with_core_technical_alignment_and_missing_optional_news_whale() -> None:
    combined = MultiFactorSignalCombiner(min_confidence=0.65).combine(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [
            intel("candle_intelligence", DecisionAction.BUY, 0.76),
            intel("order_book_intelligence", DecisionAction.BUY, 0.72),
            intel("market_structure", DecisionAction.BUY, 0.74),
            intel("whale_intelligence_v1", DecisionAction.SKIP, 0.0, missing_data=["whale_trades"]),
            intel("news_risk_intelligence", DecisionAction.SKIP, 0.0, missing_data=["news_source"]),
        ],
    )

    assert combined.final_signal == DecisionAction.BUY
    assert combined.missing_data == []
    assert combined.conflicts == []


def test_combiner_still_blocks_high_news_risk() -> None:
    combined = MultiFactorSignalCombiner(min_confidence=0.65).combine(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [
            intel("candle_intelligence", DecisionAction.BUY, 0.8),
            intel("order_book_intelligence", DecisionAction.BUY, 0.8),
            intel("market_structure", DecisionAction.BUY, 0.8),
            intel("news_risk_intelligence", DecisionAction.HOLD, 0.8, risk_score=0.8),
        ],
    )

    assert combined.final_signal == DecisionAction.SKIP
    assert combined.reason == "News or market risk is high."


def test_combiner_requires_core_technical_data() -> None:
    combined = MultiFactorSignalCombiner().combine(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        [
            intel("candle_intelligence", DecisionAction.BUY, 0.8),
            intel("news_risk_intelligence", DecisionAction.SKIP, 0.0, missing_data=["news_source"]),
        ],
    )

    assert combined.final_signal == DecisionAction.SKIP
    assert "market_structure" in combined.missing_data
    assert "order_book_intelligence" in combined.missing_data
    assert "news_source" not in combined.missing_data
