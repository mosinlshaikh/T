from __future__ import annotations

from dataclasses import asdict, dataclass

from trading_os.ai.decision_types import SignalAssessment, VerifiedDecision
from trading_os.audit.audit_logger import AuditLogger
from trading_os.intelligence.signal_combiner import CombinedSignal
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.pipeline.decision_to_trade_types import PipelineResult
from trading_os.pipeline.stages import TradeExecutionStageResult
from trading_os.risk.risk_engine import RiskDecision


@dataclass
class PipelineAuditAdapter:
    audit: AuditLogger

    def log_pipeline_result(self, result: PipelineResult) -> str:
        return self.audit.log_pipeline_result(self.result_payload(result))

    def persist_risk_result(self, risk_decision: RiskDecision) -> None:
        if self.audit.repository is not None:
            self.audit.repository.save_risk_result(risk_decision)

    def persist_zero_hallucination_result(self, decision: VerifiedDecision) -> None:
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

    def log_market_intelligence(self, signals: list[IntelligenceSignal]) -> None:
        for signal in signals:
            payload = self.intelligence_payload(signal)
            if signal.name == "candle_intelligence":
                self.audit.log_candle_analysis(payload)
            elif signal.name == "order_book_intelligence":
                self.audit.log_order_book_analysis(payload)
            elif signal.name == "whale_intelligence_v1":
                self.audit.log_whale_analysis(payload)
            elif signal.name == "news_risk_intelligence":
                self.audit.log_news_risk_analysis(payload)
            elif signal.name == "market_structure":
                self.audit.log_market_structure_analysis(payload)

    def log_combined_signal(self, combined: CombinedSignal | None) -> None:
        if combined is None:
            return
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

    def log_strategy_signals(self, symbol: str, signals: list[SignalAssessment]) -> None:
        for signal in signals:
            self.audit.log_strategy_signal(
                {
                    "symbol": symbol.upper(),
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

    def log_ai_decision(self, decision: VerifiedDecision, risk_decision: RiskDecision) -> None:
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

    def log_rejected_hallucination(self, decision: VerifiedDecision) -> None:
        self.audit.log_blocked_hallucination(
            {"symbol": decision.symbol, "reason": decision.rejection_reason}
        )

    def log_skipped_decision(self, decision: VerifiedDecision) -> None:
        self.audit.log_skipped_trade({"symbol": decision.symbol, "reason": decision.reason})

    def log_execution_result(self, execution_stage: TradeExecutionStageResult) -> None:
        for transition in execution_stage.transitions:
            self.audit.log_trade_lifecycle_transition(
                {
                    "trade_id": transition.trade_id,
                    "symbol": transition.symbol,
                    "from": transition.previous_state.value,
                    "to": transition.next_state.value,
                }
            )
        if execution_stage.status == "REJECTED_BY_RISK":
            self.audit.log_risk_rejection(
                {
                    "symbol": (
                        execution_stage.trade_context.symbol
                        if execution_stage.trade_context is not None
                        else ""
                    ),
                    "rejections": (
                        execution_stage.trade_context.risk_info.rejections
                        if execution_stage.trade_context is not None
                        else []
                    ),
                }
            )
            return
        if execution_stage.intent is not None:
            self.audit.log_execution_intent_created(asdict(execution_stage.intent))
        if execution_stage.fill is not None:
            self.audit.log_paper_order_fill(asdict(execution_stage.fill))

    def log_portfolio_snapshot(self, snapshot: object) -> None:
        self.audit.log_portfolio_snapshot(asdict(snapshot))

    @staticmethod
    def result_payload(result: PipelineResult) -> dict[str, object]:
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
            "stage_results": result.stage_results,
        }

    @staticmethod
    def intelligence_payload(signal: IntelligenceSignal) -> dict[str, object]:
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
