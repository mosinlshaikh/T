from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.decision_types import (
    DecisionAction,
    EvidenceItem,
    EvidenceType,
    SignalAssessment,
)
from trading_os.market.timeframes import Timeframe


def required_evidence() -> list[EvidenceItem]:
    return [
        EvidenceItem(EvidenceType.MARKET_TICK, "market", "price tick", 1.0),
        EvidenceItem(EvidenceType.RISK_CHECK, "risk", "risk approved", 1.0),
        EvidenceItem(EvidenceType.CAPITAL_CHECK, "capital", "capital approved", 1.0),
    ]


def signal(name: str, direction: DecisionAction, confidence: float) -> SignalAssessment:
    return SignalAssessment(
        name=name,
        direction=direction,
        confidence=confidence,
        source="test",
        evidence=required_evidence(),
    )


def test_skip_and_hold_signals_are_not_hard_conflicts() -> None:
    proposal = AIDecisionBrain(minimum_confidence=0.5).propose(
        "BTCUSDT",
        Timeframe.FIVE_MINUTES,
        required_evidence(),
        [
            signal("missing_whale", DecisionAction.SKIP, 0.3),
            signal("orderbook_neutral", DecisionAction.HOLD, 0.7),
        ],
    )

    assert proposal.action == DecisionAction.HOLD
    assert proposal.conflict_signals == []


def test_buy_signal_can_pass_with_skip_placeholders_when_confidence_is_high() -> None:
    proposal = AIDecisionBrain(minimum_confidence=0.65).propose(
        "ETHUSDT",
        Timeframe.FIVE_MINUTES,
        required_evidence(),
        [
            signal("combined_bullish", DecisionAction.BUY, 0.78),
            signal("missing_news", DecisionAction.SKIP, 0.3),
        ],
    )

    assert proposal.action == DecisionAction.BUY
    assert proposal.confidence == 0.78
    assert proposal.conflict_signals == []


def test_buy_and_sell_remain_hard_conflict() -> None:
    proposal = AIDecisionBrain(minimum_confidence=0.5).propose(
        "SOLUSDT",
        Timeframe.FIVE_MINUTES,
        required_evidence(),
        [
            signal("candle_bullish", DecisionAction.BUY, 0.8),
            signal("orderbook_bearish", DecisionAction.SELL, 0.75),
        ],
    )

    assert proposal.action == DecisionAction.HOLD
    assert proposal.conflict_signals
