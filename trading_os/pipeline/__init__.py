"""Decision-to-trade pipeline."""

from trading_os.pipeline.audit_adapter import PipelineAuditAdapter
from trading_os.pipeline.decision_to_trade import DecisionToTradePipeline, PipelineResult
from trading_os.pipeline.decision_to_trade_types import PipelineInput
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

__all__ = [
    "DecisionToTradePipeline",
    "PipelineAuditAdapter",
    "PipelineInput",
    "PipelineReasonCode",
    "PipelineResult",
    "PipelineStageName",
    "PipelineStageOutcome",
    "PipelineStageRecorder",
    "PipelineStageResult",
    "DecisionVerificationStage",
    "MarketIntelligenceStage",
    "RiskAssessmentStage",
    "ShutdownGateStage",
    "SignalCombinationStage",
    "StrategySignalStage",
    "TradeExecutionStage",
]
