from __future__ import annotations

from dataclasses import asdict, dataclass

from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.decision_types import DecisionAction, EvidenceItem, VerifiedDecision
from trading_os.ai.verified_decision_engine import VerifiedDecisionEngine
from trading_os.audit.audit_logger import AuditLogger
from trading_os.execution.intent import ExecutionIntent, ExecutionIntentLayer
from trading_os.intelligence.candle_intelligence import CandleIntelligenceEngine
from trading_os.intelligence.market_structure import MarketStructureEngine
from trading_os.intelligence.news_risk_intelligence import NewsRiskIntelligenceEngine
from trading_os.intelligence.order_book_intelligence import OrderBookIntelligenceEngine
from trading_os.intelligence.signal_combiner import MultiFactorSignalCombiner
from trading_os.intelligence.whale_intelligence_v1 import WhaleIntelligenceV1
from trading_os.market.timeframes import normalize_timeframe
from trading_os.paper.simulator import PaperFill, PaperTradingSimulator
from trading_os.pipeline.audit_adapter import PipelineAuditAdapter
from trading_os.pipeline.decision_to_trade_types import PipelineInput, PipelineResult
from trading_os.pipeline.stage_result import (
    PipelineReasonCode,
    PipelineStageName,
    PipelineStageOutcome,
    PipelineStageRecorder,
    PipelineStageResult,
)
from trading_os.pipeline.stages import (
    DecisionVerificationStage,
    MarketIntelligenceStage,
    RiskAssessmentStage,
    ShutdownGateStage,
    SignalCombinationStage,
    StrategySignalStage,
    TradeExecutionStage,
)
from trading_os.risk.capital_manager import CapitalManager
from trading_os.risk.risk_engine import RiskEngine
from trading_os.runtime.shutdown_engine import SmartShutdownEngine
from trading_os.strategies.registry import StrategyRegistry
from trading_os.trade.lifecycle import TradeContext, TradeLifecycleEngine


@dataclass
class DecisionToTradePipeline:
    strategies: StrategyRegistry
    ai_brain: AIDecisionBrain
    verifier: VerifiedDecisionEngine
    risk_engine: RiskEngine
    capital_manager: CapitalManager
    intent_layer: ExecutionIntentLayer
    paper_simulator: PaperTradingSimulator
    lifecycle: TradeLifecycleEngine
    shutdown: SmartShutdownEngine
    audit: AuditLogger
    candle_intelligence: CandleIntelligenceEngine | None = None
    order_book_intelligence: OrderBookIntelligenceEngine | None = None
    whale_intelligence: WhaleIntelligenceV1 | None = None
    news_risk_intelligence: NewsRiskIntelligenceEngine | None = None
    market_structure: MarketStructureEngine | None = None
    signal_combiner: MultiFactorSignalCombiner | None = None

    def run(
        self,
        pipeline_input: PipelineInput,
        evidence: list[EvidenceItem],
    ) -> PipelineResult:
        try:
            return self._run_impl(pipeline_input, evidence)
        except Exception as exc:
            return self._fail_closed_exception(pipeline_input, evidence, exc)

    def _run_impl(
        self,
        pipeline_input: PipelineInput,
        evidence: list[EvidenceItem],
    ) -> PipelineResult:
        recorder = PipelineStageRecorder()
        mark = recorder.mark
        stages = recorder.results
        audit = PipelineAuditAdapter(self.audit)

        shutdown_gate = ShutdownGateStage(self.shutdown).evaluate()
        if not shutdown_gate.allowed:
            decision = self._skip_decision(
                pipeline_input,
                evidence,
                shutdown_gate.reason,
            )
            mark(
                PipelineStageName.SHUTDOWN_GATE,
                PipelineStageOutcome.SKIP,
                shutdown_gate.reason_code,
            )
            result = PipelineResult(
                pipeline_input.symbol.upper(),
                pipeline_input.timeframe,
                decision,
                None,
                None,
                None,
                "BLOCKED_BY_SHUTDOWN",
                decision.reason,
                stages,
            )
            audit.log_pipeline_result(result)
            return result
        mark(PipelineStageName.SHUTDOWN_GATE, PipelineStageOutcome.CONTINUE, PipelineReasonCode.OK)

        intelligence_stage = MarketIntelligenceStage(
            candle_intelligence=self.candle_intelligence,
            order_book_intelligence=self.order_book_intelligence,
            whale_intelligence=self.whale_intelligence,
            news_risk_intelligence=self.news_risk_intelligence,
            market_structure=self.market_structure,
        ).evaluate(pipeline_input)
        intelligence_signals = intelligence_stage.signals
        audit.log_market_intelligence(intelligence_signals)
        mark(
            PipelineStageName.MARKET_INTELLIGENCE,
            PipelineStageOutcome.CONTINUE if intelligence_signals else PipelineStageOutcome.SKIP,
            intelligence_stage.reason_code,
        )
        combined_stage = SignalCombinationStage(self.signal_combiner).evaluate(
            pipeline_input,
            intelligence_signals,
        )
        combined = combined_stage.combined
        audit.log_combined_signal(combined)
        mark(
            PipelineStageName.COMBINED_SIGNAL,
            (
                PipelineStageOutcome.SKIP
                if combined_stage.reason_code == PipelineReasonCode.INSUFFICIENT_EVIDENCE
                else (
                    PipelineStageOutcome.HOLD
                    if combined_stage.reason_code == PipelineReasonCode.SIGNAL_CONFLICT
                    else PipelineStageOutcome.CONTINUE
                )
            ),
            combined_stage.reason_code,
            missing_data=combined.missing_data if combined else [],
            conflicts=combined.conflicts if combined else [],
        )

        intelligence_evidence = (
            combined.evidence
            if combined is not None
            else [item for signal in intelligence_signals for item in signal.evidence]
        )
        strategy_stage = StrategySignalStage(self.strategies).evaluate(
            pipeline_input.symbol,
            evidence + intelligence_evidence,
        )
        signals = strategy_stage.signals
        if combined is not None and not combined.missing_data:
            signals.append(combined.to_signal_assessment())
        audit.log_strategy_signals(pipeline_input.symbol, signals)
        mark(
            PipelineStageName.STRATEGY_SIGNAL,
            PipelineStageOutcome.CONTINUE if signals else PipelineStageOutcome.SKIP,
            PipelineReasonCode.OK if signals else strategy_stage.reason_code,
        )

        risk_stage = RiskAssessmentStage(self.risk_engine).evaluate(pipeline_input)
        risk_decision = risk_stage.decision
        audit.persist_risk_result(risk_decision)
        mark(
            PipelineStageName.RISK,
            PipelineStageOutcome.CONTINUE if risk_decision.allowed else PipelineStageOutcome.SKIP,
            risk_stage.reason_code,
            conflicts=risk_decision.rejections,
        )
        capital_plan = self.capital_manager.plan_paper_allocation(
            pipeline_input.symbol,
            pipeline_input.account_balance,
        )
        decision_evidence = (
            evidence
            + intelligence_evidence
            + [
                self.risk_engine.to_evidence(risk_decision),
                self.capital_manager.to_evidence(capital_plan),
            ]
        )
        decision_stage = DecisionVerificationStage(self.ai_brain, self.verifier).evaluate(
            pipeline_input,
            decision_evidence,
            signals,
        )
        proposal = decision_stage.proposal
        mark(
            PipelineStageName.AI_DECISION,
            (
                PipelineStageOutcome.HOLD
                if proposal.action == DecisionAction.HOLD
                else (
                    PipelineStageOutcome.SKIP
                    if proposal.action == DecisionAction.SKIP
                    else PipelineStageOutcome.CONTINUE
                )
            ),
            decision_stage.proposal_reason_code,
            missing_data=proposal.missing_data,
            conflicts=proposal.conflict_signals,
        )
        decision = decision_stage.decision
        mark(
            PipelineStageName.ZERO_HALLUCINATION,
            (
                PipelineStageOutcome.CONTINUE
                if decision.verified_decision
                else PipelineStageOutcome.REJECT
            ),
            decision_stage.verification_reason_code,
            missing_data=decision.missing_data,
            conflicts=decision.conflict_signals,
        )
        audit.persist_zero_hallucination_result(decision)
        audit.log_ai_decision(decision, risk_decision)

        if not decision.verified_decision:
            audit.log_rejected_hallucination(decision)
            return self._finish(
                pipeline_input,
                decision,
                None,
                None,
                None,
                "REJECTED_BY_ZERO_HALLUCINATION",
                decision.rejection_reason,
                stages,
            )

        if decision.action in {DecisionAction.HOLD, DecisionAction.SKIP}:
            audit.log_skipped_decision(decision)
            return self._finish(
                pipeline_input,
                decision,
                None,
                None,
                None,
                decision.action.value,
                decision.reason,
                stages,
            )

        execution_stage = TradeExecutionStage(
            self.lifecycle,
            self.intent_layer,
            self.paper_simulator,
        ).evaluate(pipeline_input, decision, risk_decision)
        audit.log_execution_result(execution_stage)
        mark(
            PipelineStageName.TRADE_LIFECYCLE,
            (
                PipelineStageOutcome.SKIP
                if execution_stage.status == "REJECTED_BY_RISK"
                else PipelineStageOutcome.CONTINUE
            ),
            execution_stage.lifecycle_reason_code,
            conflicts=risk_decision.rejections,
        )
        mark(
            PipelineStageName.EXECUTION_INTENT,
            (
                PipelineStageOutcome.SKIP
                if execution_stage.intent is None
                else PipelineStageOutcome.CONTINUE
            ),
            execution_stage.intent_reason_code,
        )
        mark(
            PipelineStageName.PAPER_EXECUTION,
            (
                PipelineStageOutcome.SKIP
                if execution_stage.fill is None
                else PipelineStageOutcome.CONTINUE
            ),
            execution_stage.paper_reason_code,
        )

        if execution_stage.status == "REJECTED_BY_RISK":
            return self._finish(
                pipeline_input,
                decision,
                execution_stage.trade_context,
                None,
                None,
                execution_stage.status,
                execution_stage.reason,
                stages,
            )

        if execution_stage.intent is None:
            return self._finish(
                pipeline_input,
                decision,
                execution_stage.trade_context,
                None,
                None,
                execution_stage.status,
                execution_stage.reason,
                stages,
            )

        if execution_stage.fill is not None:
            audit.log_portfolio_snapshot(self.paper_simulator.portfolio.wallet_snapshot())
        return self._finish(
            pipeline_input,
            decision,
            execution_stage.trade_context,
            execution_stage.intent,
            execution_stage.fill,
            execution_stage.status,
            execution_stage.reason,
            stages,
        )

    def _fail_closed_exception(
        self,
        pipeline_input: PipelineInput,
        evidence: list[EvidenceItem],
        exc: Exception,
    ) -> PipelineResult:
        stage = asdict(
            PipelineStageResult(
                stage=PipelineStageName.PIPELINE_EXCEPTION,
                outcome=PipelineStageOutcome.SKIP,
                reason_code=PipelineReasonCode.INTERNAL_EXCEPTION,
                latency_ms=0.0,
                missing_data=[],
                conflicts=[exc.__class__.__name__],
            )
        )
        decision = VerifiedDecision(
            symbol=pipeline_input.symbol.upper(),
            timeframe=pipeline_input.timeframe,
            action=DecisionAction.SKIP,
            confidence=0.0,
            evidence=evidence,
            reason="Internal decision-path exception; failed closed to SKIP.",
            missing_data=[],
            conflict_signals=[],
            verified_decision=False,
            rejection_reason="INTERNAL_EXCEPTION",
        )
        result = PipelineResult(
            symbol=pipeline_input.symbol.upper(),
            timeframe=pipeline_input.timeframe,
            decision=decision,
            trade_context=None,
            execution_intent=None,
            paper_fill=None,
            status="SKIP",
            reason=decision.reason,
            stage_results=[stage],
        )
        try:
            audit = PipelineAuditAdapter(self.audit)
            audit.log_pipeline_result(result)
            self.audit.log_skipped_trade(
                {
                    "symbol": decision.symbol,
                    "reason": decision.reason,
                    "reason_code": PipelineReasonCode.INTERNAL_EXCEPTION.value,
                    "exception_type": exc.__class__.__name__,
                }
            )
        except Exception:
            pass
        return result

    def _finish(
        self,
        pipeline_input: PipelineInput,
        decision: VerifiedDecision,
        trade_context: TradeContext | None,
        intent: ExecutionIntent | None,
        fill: PaperFill | None,
        status: str,
        reason: str,
        stage_results: list[dict[str, object]] | None = None,
    ) -> PipelineResult:
        result = PipelineResult(
            symbol=pipeline_input.symbol.upper(),
            timeframe=pipeline_input.timeframe,
            decision=decision,
            trade_context=trade_context,
            execution_intent=intent,
            paper_fill=fill,
            status=status,
            reason=reason,
            stage_results=stage_results or [],
        )
        PipelineAuditAdapter(self.audit).log_pipeline_result(result)
        return result

    def _skip_decision(
        self,
        pipeline_input: PipelineInput,
        evidence: list[EvidenceItem],
        reason: str,
    ) -> VerifiedDecision:
        proposal = self.ai_brain.propose(
            pipeline_input.symbol,
            pipeline_input.timeframe,
            evidence,
            [],
        )
        return VerifiedDecision(
            symbol=pipeline_input.symbol.upper(),
            timeframe=pipeline_input.timeframe,
            action=DecisionAction.SKIP,
            confidence=0.0,
            evidence=evidence,
            reason=reason,
            missing_data=proposal.missing_data,
            conflict_signals=[],
            verified_decision=False,
            rejection_reason=reason,
        )

    @staticmethod
    def build_input(
        symbol: str,
        timeframe: str,
        market_price: float,
        quantity: float,
        stop_loss: float,
        take_profit: float,
        account_balance: float,
    ) -> PipelineInput:
        return PipelineInput(
            symbol=symbol.upper(),
            timeframe=normalize_timeframe(timeframe),
            market_price=market_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            account_balance=account_balance,
        )
