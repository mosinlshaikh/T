from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.decision_types import (
    DecisionAction,
    DecisionProposal,
    EvidenceItem,
    SignalAssessment,
    VerifiedDecision,
)
from trading_os.ai.verified_decision_engine import VerifiedDecisionEngine
from trading_os.execution.intent import ExecutionIntent, ExecutionIntentLayer
from trading_os.intelligence.candle_intelligence import CandleIntelligenceEngine
from trading_os.intelligence.market_structure import MarketStructureEngine
from trading_os.intelligence.news_risk_intelligence import NewsRiskIntelligenceEngine
from trading_os.intelligence.order_book_intelligence import OrderBookIntelligenceEngine
from trading_os.intelligence.signal_combiner import CombinedSignal, MultiFactorSignalCombiner
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.intelligence.whale_intelligence_v1 import WhaleIntelligenceV1
from trading_os.paper.simulator import PaperFill, PaperTradingSimulator
from trading_os.pipeline.decision_to_trade_types import PipelineInput
from trading_os.pipeline.stage_result import PipelineReasonCode, normalize_reason_code
from trading_os.risk.risk_engine import RiskContext, RiskDecision, RiskEngine
from trading_os.runtime.shutdown_engine import SmartShutdownEngine
from trading_os.strategies.registry import StrategyRegistry
from trading_os.trade.lifecycle import RiskInfo, TradeContext, TradeLifecycleEngine, TradeState


@dataclass(frozen=True)
class GateStageResult:
    allowed: bool
    reason_code: PipelineReasonCode
    reason: str


@dataclass(frozen=True)
class RiskStageResult:
    decision: RiskDecision
    context: RiskContext
    reason_code: PipelineReasonCode


@dataclass(frozen=True)
class MarketIntelligenceStageResult:
    signals: list[IntelligenceSignal]
    reason_code: PipelineReasonCode


@dataclass(frozen=True)
class StrategySignalStageResult:
    signals: list[SignalAssessment]
    reason_code: PipelineReasonCode


@dataclass(frozen=True)
class SignalCombinationStageResult:
    combined: CombinedSignal | None
    reason_code: PipelineReasonCode


@dataclass(frozen=True)
class DecisionVerificationStageResult:
    proposal: DecisionProposal
    decision: VerifiedDecision
    proposal_reason_code: PipelineReasonCode
    verification_reason_code: PipelineReasonCode


@dataclass(frozen=True)
class TradeLifecycleTransition:
    trade_id: str
    symbol: str
    previous_state: TradeState
    next_state: TradeState


@dataclass(frozen=True)
class TradeExecutionStageResult:
    trade_context: TradeContext | None
    intent: ExecutionIntent | None
    fill: PaperFill | None
    status: str
    reason: str
    lifecycle_reason_code: PipelineReasonCode
    intent_reason_code: PipelineReasonCode
    paper_reason_code: PipelineReasonCode
    transitions: list[TradeLifecycleTransition]


class ShutdownGateStage:
    def __init__(self, shutdown: SmartShutdownEngine) -> None:
        self.shutdown = shutdown

    def evaluate(self) -> GateStageResult:
        if self.shutdown.accepts_new_trades:
            return GateStageResult(True, PipelineReasonCode.OK, "Shutdown gate passed.")
        return GateStageResult(
            False,
            PipelineReasonCode.SHUTDOWN_REQUESTED,
            "Shutdown requested; new trade intents are blocked.",
        )


class RiskAssessmentStage:
    def __init__(self, risk_engine: RiskEngine) -> None:
        self.risk_engine = risk_engine

    def evaluate(self, pipeline_input: PipelineInput) -> RiskStageResult:
        context = RiskContext(
            symbol=pipeline_input.symbol,
            account_balance=pipeline_input.account_balance,
            requested_trade_size=pipeline_input.quantity * pipeline_input.market_price,
            current_exposure=pipeline_input.current_exposure,
            daily_realized_loss=pipeline_input.daily_realized_loss,
            consecutive_losses=pipeline_input.consecutive_losses,
            minutes_since_last_loss=pipeline_input.minutes_since_last_loss,
            stop_loss_present=pipeline_input.stop_loss > 0,
            take_profit_present=pipeline_input.take_profit > 0,
        )
        decision = self.risk_engine.evaluate(context)
        return RiskStageResult(
            decision=decision,
            context=context,
            reason_code=(
                PipelineReasonCode.RISK_APPROVED
                if decision.allowed
                else PipelineReasonCode.RISK_REJECTED
            ),
        )


@dataclass
class MarketIntelligenceStage:
    candle_intelligence: CandleIntelligenceEngine | None = None
    order_book_intelligence: OrderBookIntelligenceEngine | None = None
    whale_intelligence: WhaleIntelligenceV1 | None = None
    news_risk_intelligence: NewsRiskIntelligenceEngine | None = None
    market_structure: MarketStructureEngine | None = None

    def evaluate(self, pipeline_input: PipelineInput) -> MarketIntelligenceStageResult:
        signals: list[IntelligenceSignal] = []
        if self.candle_intelligence is not None:
            signals.append(
                self.candle_intelligence.analyze(
                    pipeline_input.symbol,
                    pipeline_input.timeframe,
                    pipeline_input.candles or [],
                )
            )
        if self.order_book_intelligence is not None:
            signals.append(
                self.order_book_intelligence.analyze(
                    pipeline_input.symbol,
                    pipeline_input.timeframe,
                    pipeline_input.order_book,
                )
            )
        if self.whale_intelligence is not None:
            signals.append(
                self.whale_intelligence.analyze(
                    pipeline_input.symbol,
                    pipeline_input.timeframe,
                    pipeline_input.whale_trades,
                )
            )
        if self.news_risk_intelligence is not None:
            signals.append(
                self.news_risk_intelligence.analyze(
                    pipeline_input.symbol,
                    pipeline_input.timeframe,
                    pipeline_input.news_items,
                )
            )
        if self.market_structure is not None:
            signals.append(
                self.market_structure.analyze(
                    pipeline_input.symbol,
                    pipeline_input.timeframe,
                    pipeline_input.candles or [],
                )
            )
        return MarketIntelligenceStageResult(
            signals=signals,
            reason_code=(
                PipelineReasonCode.OK if signals else PipelineReasonCode.NO_INTELLIGENCE_SIGNALS
            ),
        )


class StrategySignalStage:
    def __init__(self, strategies: StrategyRegistry) -> None:
        self.strategies = strategies

    def evaluate(
        self,
        symbol: str,
        evidence: list[EvidenceItem],
    ) -> StrategySignalStageResult:
        signals = self.strategies.evaluate_all(symbol, evidence)
        return StrategySignalStageResult(
            signals=signals,
            reason_code=(
                PipelineReasonCode.OK if signals else PipelineReasonCode.NO_STRATEGY_SIGNALS
            ),
        )


class SignalCombinationStage:
    def __init__(self, signal_combiner: MultiFactorSignalCombiner | None) -> None:
        self.signal_combiner = signal_combiner

    def evaluate(
        self,
        pipeline_input: PipelineInput,
        intelligence_signals: list[IntelligenceSignal],
    ) -> SignalCombinationStageResult:
        if self.signal_combiner is None:
            return SignalCombinationStageResult(None, PipelineReasonCode.NO_COMBINER_CONFIGURED)
        if not intelligence_signals:
            return SignalCombinationStageResult(None, PipelineReasonCode.NO_INTELLIGENCE_SIGNALS)

        combined = self.signal_combiner.combine(
            pipeline_input.symbol,
            pipeline_input.timeframe,
            intelligence_signals,
        )
        if combined.missing_data:
            reason_code = PipelineReasonCode.INSUFFICIENT_EVIDENCE
        elif combined.conflicts:
            reason_code = PipelineReasonCode.SIGNAL_CONFLICT
        else:
            reason_code = PipelineReasonCode.OK
        return SignalCombinationStageResult(combined, reason_code)


class DecisionVerificationStage:
    def __init__(
        self,
        ai_brain: AIDecisionBrain,
        verifier: VerifiedDecisionEngine,
    ) -> None:
        self.ai_brain = ai_brain
        self.verifier = verifier

    def evaluate(
        self,
        pipeline_input: PipelineInput,
        evidence: list[EvidenceItem],
        signals: list[SignalAssessment],
    ) -> DecisionVerificationStageResult:
        proposal = self.ai_brain.propose(
            pipeline_input.symbol,
            pipeline_input.timeframe,
            evidence,
            signals,
        )
        decision = self.verifier.verify(proposal)
        return DecisionVerificationStageResult(
            proposal=proposal,
            decision=decision,
            proposal_reason_code=normalize_reason_code(proposal.reason),
            verification_reason_code=(
                PipelineReasonCode.ZERO_HALLUCINATION_VERIFIED
                if decision.verified_decision
                else PipelineReasonCode.ZERO_HALLUCINATION_REJECTED
            ),
        )


class TradeExecutionStage:
    def __init__(
        self,
        lifecycle: TradeLifecycleEngine,
        intent_layer: ExecutionIntentLayer,
        paper_simulator: PaperTradingSimulator,
    ) -> None:
        self.lifecycle = lifecycle
        self.intent_layer = intent_layer
        self.paper_simulator = paper_simulator

    def evaluate(
        self,
        pipeline_input: PipelineInput,
        decision: VerifiedDecision,
        risk_decision: RiskDecision,
    ) -> TradeExecutionStageResult:
        if decision.action not in {DecisionAction.BUY, DecisionAction.SELL}:
            return TradeExecutionStageResult(
                trade_context=None,
                intent=None,
                fill=None,
                status=decision.action.value,
                reason=decision.reason,
                lifecycle_reason_code=PipelineReasonCode.NO_ACTIONABLE_DIRECTION,
                intent_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                paper_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                transitions=[],
            )

        transitions: list[TradeLifecycleTransition] = []
        trade_context = TradeContext(
            symbol=decision.symbol,
            timeframe=decision.timeframe,
            side=decision.action.value,
            entry=pipeline_input.market_price,
            stop_loss=pipeline_input.stop_loss,
            take_profit=pipeline_input.take_profit,
            confidence=decision.confidence,
            evidence=decision.evidence,
            risk_info=RiskInfo(
                approved=risk_decision.allowed,
                risk_approval_id=f"risk:{decision.timestamp}",
                reason=risk_decision.reason,
                rejections=risk_decision.rejections,
            ),
        )
        trade_context = self._transition(
            trade_context,
            TradeState.RISK_CHECK_PENDING,
            transitions,
        )

        if not risk_decision.allowed:
            rejected = self._transition(
                trade_context,
                TradeState.REJECTED_BY_RISK,
                transitions,
            )
            return TradeExecutionStageResult(
                trade_context=rejected,
                intent=None,
                fill=None,
                status="REJECTED_BY_RISK",
                reason=risk_decision.reason,
                lifecycle_reason_code=PipelineReasonCode.RISK_REJECTED,
                intent_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                paper_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                transitions=transitions,
            )

        approved = self._transition(
            trade_context,
            TradeState.APPROVED_FOR_PAPER,
            transitions,
        )
        intent = self.intent_layer.from_verified_decision(
            decision,
            approved,
            pipeline_input.quantity,
        )
        if intent is None:
            return TradeExecutionStageResult(
                trade_context=approved,
                intent=None,
                fill=None,
                status="NO_INTENT",
                reason="Decision did not produce an execution intent.",
                lifecycle_reason_code=PipelineReasonCode.RISK_APPROVED,
                intent_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                paper_reason_code=PipelineReasonCode.NO_EXECUTION_INTENT,
                transitions=transitions,
            )

        paper_open = self._transition(approved, TradeState.PAPER_OPEN, transitions)
        fill = self.paper_simulator.open_trade(intent, pipeline_input.market_price)
        return TradeExecutionStageResult(
            trade_context=paper_open,
            intent=intent,
            fill=fill,
            status="PAPER_OPEN",
            reason="Paper trade opened.",
            lifecycle_reason_code=PipelineReasonCode.RISK_APPROVED,
            intent_reason_code=PipelineReasonCode.EXECUTION_INTENT_CREATED,
            paper_reason_code=PipelineReasonCode.PAPER_TRADE_OPENED,
            transitions=transitions,
        )

    def _transition(
        self,
        context: TradeContext,
        target: TradeState,
        transitions: list[TradeLifecycleTransition],
    ) -> TradeContext:
        previous = context.state
        updated = self.lifecycle.transition(context, target)
        transitions.append(
            TradeLifecycleTransition(
                trade_id=updated.trade_id,
                symbol=updated.symbol,
                previous_state=previous,
                next_state=updated.state,
            )
        )
        return updated
