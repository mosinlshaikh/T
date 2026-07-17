from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.decision_types import (
    DecisionAction,
    EvidenceItem,
    EvidenceType,
    SignalAssessment,
    VerifiedDecision,
)
from trading_os.ai.verified_decision_engine import VerifiedDecisionEngine
from trading_os.execution.intent import ExecutionIntentLayer
from trading_os.intelligence.signal_combiner import MultiFactorSignalCombiner
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.timeframes import Timeframe
from trading_os.paper.simulator import PaperTradingSimulator
from trading_os.pipeline.decision_to_trade_types import PipelineInput
from trading_os.pipeline.stage_result import PipelineReasonCode
from trading_os.pipeline.stages import (
    DecisionVerificationStage,
    MarketIntelligenceStage,
    RiskAssessmentStage,
    ShutdownGateStage,
    SignalCombinationStage,
    StrategySignalStage,
    TradeExecutionStage,
)
from trading_os.risk.risk_engine import RiskDecision, RiskEngine
from trading_os.runtime.shutdown_engine import SmartShutdownEngine
from trading_os.strategies.registry import StrategyRegistry
from trading_os.trade.lifecycle import TradeLifecycleEngine, TradeState


def test_shutdown_gate_blocks_new_trades_when_shutdown_requested() -> None:
    shutdown = SmartShutdownEngine()
    shutdown.request_shutdown(active_trade_count=0)

    result = ShutdownGateStage(shutdown).evaluate()

    assert result.allowed is False
    assert result.reason_code == PipelineReasonCode.SHUTDOWN_REQUESTED
    assert "blocked" in result.reason.lower()


def test_shutdown_gate_allows_running_state() -> None:
    result = ShutdownGateStage(SmartShutdownEngine()).evaluate()

    assert result.allowed is True
    assert result.reason_code == PipelineReasonCode.OK


def test_risk_stage_builds_context_and_rejects_missing_stop_loss() -> None:
    result = RiskAssessmentStage(RiskEngine()).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=0.0,
            take_profit=101.5,
            account_balance=10_000.0,
        )
    )

    assert result.reason_code == PipelineReasonCode.RISK_REJECTED
    assert result.decision.allowed is False
    assert "Stop-loss is required." in result.decision.rejections
    assert result.context.requested_trade_size == 10.0


def test_risk_stage_approves_safe_paper_context() -> None:
    result = RiskAssessmentStage(RiskEngine()).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        )
    )

    assert result.reason_code == PipelineReasonCode.RISK_APPROVED
    assert result.decision.allowed is True


def test_market_intelligence_stage_without_engines_returns_no_signals() -> None:
    result = MarketIntelligenceStage().evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        )
    )

    assert result.signals == []
    assert result.reason_code == PipelineReasonCode.NO_INTELLIGENCE_SIGNALS


def test_strategy_signal_stage_without_matching_evidence_returns_no_signals() -> None:
    result = StrategySignalStage(StrategyRegistry.with_default_placeholders()).evaluate(
        "BTCUSDT",
        [],
    )

    assert result.signals == []
    assert result.reason_code == PipelineReasonCode.NO_STRATEGY_SIGNALS


def test_signal_combination_stage_skips_without_combiner() -> None:
    result = SignalCombinationStage(None).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        ),
        [],
    )

    assert result.combined is None
    assert result.reason_code == PipelineReasonCode.NO_COMBINER_CONFIGURED


def test_signal_combination_stage_reports_missing_required_intelligence() -> None:
    evidence = EvidenceItem(EvidenceType.CANDLE, "candles", "candle evidence", 0.8)
    result = SignalCombinationStage(MultiFactorSignalCombiner()).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        ),
        [
            IntelligenceSignal(
                name="candle_intelligence",
                symbol="BTCUSDT",
                timeframe=Timeframe.FIVE_MINUTES,
                direction=DecisionAction.BUY,
                confidence=0.8,
                evidence=[evidence],
            )
        ],
    )

    assert result.combined is not None
    assert result.combined.final_signal == DecisionAction.SKIP
    assert result.reason_code == PipelineReasonCode.INSUFFICIENT_EVIDENCE
    assert "market_structure" in result.combined.missing_data


def test_decision_verification_stage_returns_verified_buy_with_required_evidence() -> None:
    evidence = [
        EvidenceItem(EvidenceType.MARKET_TICK, "market", "price tick", 1.0),
        EvidenceItem(EvidenceType.RISK_CHECK, "risk", "risk approved", 1.0),
        EvidenceItem(EvidenceType.CAPITAL_CHECK, "capital", "capital approved", 1.0),
    ]
    signals = [
        SignalAssessment(
            name="test_signal",
            direction=DecisionAction.BUY,
            confidence=0.8,
            source="unit_test",
            evidence=evidence,
        )
    ]

    result = DecisionVerificationStage(AIDecisionBrain(), VerifiedDecisionEngine()).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        ),
        evidence,
        signals,
    )

    assert result.decision.action == DecisionAction.BUY
    assert result.decision.verified_decision is True
    assert result.proposal_reason_code == PipelineReasonCode.OK
    assert result.verification_reason_code == PipelineReasonCode.ZERO_HALLUCINATION_VERIFIED


def test_trade_execution_stage_opens_approved_paper_trade() -> None:
    evidence = [
        EvidenceItem(EvidenceType.MARKET_TICK, "market", "price tick", 1.0),
        EvidenceItem(EvidenceType.RISK_CHECK, "risk", "risk approved", 1.0),
        EvidenceItem(EvidenceType.CAPITAL_CHECK, "capital", "capital approved", 1.0),
    ]
    decision = VerifiedDecision(
        symbol="BTCUSDT",
        timeframe=Timeframe.FIVE_MINUTES,
        action=DecisionAction.BUY,
        confidence=0.8,
        evidence=evidence,
        reason="Decision proposal based on aligned evidence.",
        missing_data=[],
        conflict_signals=[],
        verified_decision=True,
    )

    result = TradeExecutionStage(
        TradeLifecycleEngine(),
        ExecutionIntentLayer(),
        PaperTradingSimulator(),
    ).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        ),
        decision,
        RiskDecision(True, "Risk check passed.", []),
    )

    assert result.status == "PAPER_OPEN"
    assert result.trade_context is not None
    assert result.trade_context.state == TradeState.PAPER_OPEN
    assert result.intent is not None
    assert result.intent.live_enabled is False
    assert result.fill is not None
    assert result.paper_reason_code == PipelineReasonCode.PAPER_TRADE_OPENED


def test_trade_execution_stage_rejects_risk_before_intent() -> None:
    decision = VerifiedDecision(
        symbol="BTCUSDT",
        timeframe=Timeframe.FIVE_MINUTES,
        action=DecisionAction.BUY,
        confidence=0.8,
        evidence=[EvidenceItem(EvidenceType.MARKET_TICK, "market", "price tick", 1.0)],
        reason="Decision proposal based on aligned evidence.",
        missing_data=[],
        conflict_signals=[],
        verified_decision=True,
    )

    result = TradeExecutionStage(
        TradeLifecycleEngine(),
        ExecutionIntentLayer(),
        PaperTradingSimulator(),
    ).evaluate(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=100.0,
            quantity=0.1,
            stop_loss=99.0,
            take_profit=101.5,
            account_balance=10_000.0,
        ),
        decision,
        RiskDecision(False, "Risk rejected.", ["test rejection"]),
    )

    assert result.status == "REJECTED_BY_RISK"
    assert result.trade_context is not None
    assert result.trade_context.state == TradeState.REJECTED_BY_RISK
    assert result.intent is None
    assert result.fill is None
    assert result.lifecycle_reason_code == PipelineReasonCode.RISK_REJECTED
