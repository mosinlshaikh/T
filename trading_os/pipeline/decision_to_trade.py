from __future__ import annotations

from dataclasses import asdict, dataclass

from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.decision_types import DecisionAction, EvidenceItem, VerifiedDecision
from trading_os.ai.verified_decision_engine import VerifiedDecisionEngine
from trading_os.audit.audit_logger import AuditLogger
from trading_os.execution.intent import ExecutionIntent, ExecutionIntentLayer
from trading_os.intelligence.candle_intelligence import CandleIntelligenceEngine
from trading_os.intelligence.market_structure import MarketStructureEngine
from trading_os.intelligence.news_risk_intelligence import NewsItem, NewsRiskIntelligenceEngine
from trading_os.intelligence.order_book_intelligence import OrderBookIntelligenceEngine
from trading_os.intelligence.signal_combiner import MultiFactorSignalCombiner
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.intelligence.whale_intelligence_v1 import WhaleIntelligenceV1, WhaleTrade
from trading_os.market.candle_engine import Candle
from trading_os.market.order_book_engine import OrderBookSnapshot
from trading_os.market.timeframes import Timeframe, normalize_timeframe
from trading_os.paper.simulator import PaperFill, PaperTradingSimulator
from trading_os.risk.capital_manager import CapitalManager
from trading_os.risk.risk_engine import RiskContext, RiskEngine
from trading_os.runtime.shutdown_engine import SmartShutdownEngine
from trading_os.strategies.registry import StrategyRegistry
from trading_os.trade.lifecycle import RiskInfo, TradeContext, TradeLifecycleEngine, TradeState


@dataclass(frozen=True)
class PipelineInput:
    symbol: str
    timeframe: Timeframe
    market_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    account_balance: float
    current_exposure: float = 0.0
    daily_realized_loss: float = 0.0
    consecutive_losses: int = 0
    minutes_since_last_loss: int | None = None
    candles: list[Candle] | None = None
    order_book: OrderBookSnapshot | None = None
    whale_trades: list[WhaleTrade] | None = None
    news_items: list[NewsItem] | None = None


@dataclass(frozen=True)
class PipelineResult:
    symbol: str
    timeframe: Timeframe
    decision: VerifiedDecision
    trade_context: TradeContext | None
    execution_intent: ExecutionIntent | None
    paper_fill: PaperFill | None
    status: str
    reason: str


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
        if not self.shutdown.accepts_new_trades:
            decision = self._skip_decision(
                pipeline_input,
                evidence,
                "Shutdown requested; new trade intents are blocked.",
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
            )
            self.audit.log_pipeline_result(self._result_payload(result))
            return result

        intelligence_signals = self._market_intelligence(pipeline_input)
        combined = None
        if self.signal_combiner is not None and intelligence_signals:
            combined = self.signal_combiner.combine(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                intelligence_signals,
            )
            self.audit.log_combined_signal_result(
                {
                    "symbol": combined.symbol,
                    "timeframe": combined.timeframe.value,
                    "final_signal": combined.final_signal.value,
                    "confidence_score": combined.confidence_score,
                    "risk_score": combined.risk_score,
                    "missing_data": combined.missing_data,
                    "conflicts": combined.conflicts,
                }
            )
            if combined.missing_data:
                self.audit.log_missing_data(
                    {"symbol": combined.symbol, "missing_data": combined.missing_data}
                )
            if combined.conflicts:
                self.audit.log_conflict_reason(
                    {"symbol": combined.symbol, "conflicts": combined.conflicts}
                )

        intelligence_evidence = (
            combined.evidence
            if combined is not None
            else [item for signal in intelligence_signals for item in signal.evidence]
        )
        signals = self.strategies.evaluate_all(
            pipeline_input.symbol,
            evidence + intelligence_evidence,
        )
        if combined is not None and not combined.missing_data:
            signals.append(combined.to_signal_assessment())
        for signal in signals:
            self.audit.log_strategy_signal(
                {
                    "symbol": pipeline_input.symbol.upper(),
                    "signal": signal.name,
                    "source": signal.source,
                    "direction": signal.direction.value,
                    "confidence": signal.confidence,
                    "evidence_count": len(signal.evidence),
                    "evidence_sources": [item.source for item in signal.evidence],
                    "live_trading_enabled": False,
                    "public_data_only": True,
                }
            )

        risk_decision = self.risk_engine.evaluate(
            RiskContext(
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
        )
        if self.audit.repository is not None:
            self.audit.repository.save_risk_result(risk_decision)
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
        proposal = self.ai_brain.propose(
            pipeline_input.symbol,
            pipeline_input.timeframe,
            decision_evidence,
            signals,
        )
        decision = self.verifier.verify(proposal)
        if self.audit.repository is not None:
            self.audit.repository.save_zero_hallucination_result(
                {
                    "symbol": decision.symbol,
                    "action": decision.action.value,
                    "verified_decision": decision.verified_decision,
                    "rejection_reason": decision.rejection_reason,
                    "timestamp": decision.timestamp,
                }
            )
        self.audit.log_ai_decision(
            {
                "symbol": decision.symbol,
                "action": decision.action.value,
                "confidence": decision.confidence,
                "evidence": [
                    {
                        "type": item.evidence_type.value,
                        "source": item.source,
                        "summary": item.summary,
                        "confidence": item.confidence,
                        "timestamp": item.timestamp,
                    }
                    for item in decision.evidence
                ],
                "verified": decision.verified_decision,
                "reason": decision.reason,
                "missing_data": decision.missing_data,
                "conflict_signals": decision.conflict_signals,
                "risk_status": "approved" if risk_decision.allowed else "rejected",
                "rejection_reason": decision.rejection_reason,
            }
        )

        if not decision.verified_decision:
            self.audit.log_blocked_hallucination(
                {"symbol": decision.symbol, "reason": decision.rejection_reason}
            )
            return self._finish(
                pipeline_input,
                decision,
                None,
                None,
                None,
                "REJECTED_BY_ZERO_HALLUCINATION",
                decision.rejection_reason,
            )

        if decision.action in {DecisionAction.HOLD, DecisionAction.SKIP}:
            self.audit.log_skipped_trade({"symbol": decision.symbol, "reason": decision.reason})
            return self._finish(
                pipeline_input,
                decision,
                None,
                None,
                None,
                decision.action.value,
                decision.reason,
            )

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
        trade_context = self._transition(trade_context, TradeState.RISK_CHECK_PENDING)

        if not risk_decision.allowed:
            rejected = self._transition(trade_context, TradeState.REJECTED_BY_RISK)
            self.audit.log_risk_rejection(
                {"symbol": decision.symbol, "rejections": risk_decision.rejections}
            )
            return self._finish(
                pipeline_input,
                decision,
                rejected,
                None,
                None,
                "REJECTED_BY_RISK",
                risk_decision.reason,
            )

        approved = self._transition(trade_context, TradeState.APPROVED_FOR_PAPER)
        intent = self.intent_layer.from_verified_decision(
            decision, approved, pipeline_input.quantity
        )
        if intent is None:
            return self._finish(
                pipeline_input,
                decision,
                approved,
                None,
                None,
                "NO_INTENT",
                "Decision did not produce an execution intent.",
            )

        self.audit.log_execution_intent_created(asdict(intent))
        paper_open = self._transition(approved, TradeState.PAPER_OPEN)
        fill = self.paper_simulator.open_trade(intent, pipeline_input.market_price)
        self.audit.log_paper_order_fill(asdict(fill))
        self.audit.log_portfolio_snapshot(asdict(self.paper_simulator.portfolio.wallet_snapshot()))
        return self._finish(
            pipeline_input,
            decision,
            paper_open,
            intent,
            fill,
            "PAPER_OPEN",
            "Paper trade opened.",
        )

    def _finish(
        self,
        pipeline_input: PipelineInput,
        decision: VerifiedDecision,
        trade_context: TradeContext | None,
        intent: ExecutionIntent | None,
        fill: PaperFill | None,
        status: str,
        reason: str,
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
        )
        self.audit.log_pipeline_result(self._result_payload(result))
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

    def _transition(self, context: TradeContext, target: TradeState) -> TradeContext:
        previous = context.state
        updated = self.lifecycle.transition(context, target)
        self.audit.log_trade_lifecycle_transition(
            {
                "trade_id": updated.trade_id,
                "symbol": updated.symbol,
                "from": previous.value,
                "to": updated.state.value,
            }
        )
        return updated

    def _market_intelligence(self, pipeline_input: PipelineInput) -> list[IntelligenceSignal]:
        signals: list[IntelligenceSignal] = []
        if self.candle_intelligence is not None:
            signal = self.candle_intelligence.analyze(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                pipeline_input.candles or [],
            )
            signals.append(signal)
            self.audit.log_candle_analysis(self._intelligence_payload(signal))
        if self.order_book_intelligence is not None:
            signal = self.order_book_intelligence.analyze(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                pipeline_input.order_book,
            )
            signals.append(signal)
            self.audit.log_order_book_analysis(self._intelligence_payload(signal))
        if self.whale_intelligence is not None:
            signal = self.whale_intelligence.analyze(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                pipeline_input.whale_trades,
            )
            signals.append(signal)
            self.audit.log_whale_analysis(self._intelligence_payload(signal))
        if self.news_risk_intelligence is not None:
            signal = self.news_risk_intelligence.analyze(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                pipeline_input.news_items,
            )
            signals.append(signal)
            self.audit.log_news_risk_analysis(self._intelligence_payload(signal))
        if self.market_structure is not None:
            signal = self.market_structure.analyze(
                pipeline_input.symbol,
                pipeline_input.timeframe,
                pipeline_input.candles or [],
            )
            signals.append(signal)
            self.audit.log_market_structure_analysis(self._intelligence_payload(signal))
        return signals

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

    @staticmethod
    def _result_payload(result: PipelineResult) -> dict[str, object]:
        return {
            "symbol": result.symbol,
            "timeframe": result.timeframe.value,
            "status": result.status,
            "reason": result.reason,
            "decision": result.decision.action.value,
            "verified": result.decision.verified_decision,
            "intent_id": result.execution_intent.intent_id if result.execution_intent else "",
            "fill_id": result.paper_fill.fill_id if result.paper_fill else "",
            "trade_id": result.trade_context.trade_id if result.trade_context else "",
        }

    @staticmethod
    def _intelligence_payload(signal: IntelligenceSignal) -> dict[str, object]:
        return {
            "name": signal.name,
            "symbol": signal.symbol,
            "timeframe": signal.timeframe.value,
            "direction": signal.direction.value,
            "confidence": signal.confidence,
            "missing_data": signal.missing_data,
            "conflicts": signal.conflicts,
            "risk_score": signal.risk_score,
            "reason": signal.reason,
        }
