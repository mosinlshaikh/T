from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from time import perf_counter


class PipelineStageOutcome(str, Enum):
    CONTINUE = "CONTINUE"
    HOLD = "HOLD"
    SKIP = "SKIP"
    REJECT = "REJECT"
    APPROVE_PROPOSAL = "APPROVE_PROPOSAL"


class PipelineStageName(str, Enum):
    SHUTDOWN_GATE = "shutdown_gate"
    MARKET_INTELLIGENCE = "market_intelligence"
    COMBINED_SIGNAL = "combined_signal"
    STRATEGY_SIGNAL = "strategy_signal"
    RISK = "risk"
    AI_DECISION = "ai_decision"
    ZERO_HALLUCINATION = "zero_hallucination"
    TRADE_LIFECYCLE = "trade_lifecycle"
    EXECUTION_INTENT = "execution_intent"
    PAPER_EXECUTION = "paper_execution"
    PIPELINE_EXCEPTION = "pipeline_exception"


class PipelineReasonCode(str, Enum):
    OK = "OK"
    NO_DATA = "NO_DATA"
    STALE_DATA = "STALE_DATA"
    INVALID_SCHEMA = "INVALID_SCHEMA"
    TIMESTAMP_GAP = "TIMESTAMP_GAP"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_COMBINER_CONFIGURED = "NO_COMBINER_CONFIGURED"
    NO_INTELLIGENCE_SIGNALS = "NO_INTELLIGENCE_SIGNALS"
    NO_STRATEGY_SIGNALS = "NO_STRATEGY_SIGNALS"
    SIGNAL_CONFLICT = "SIGNAL_CONFLICT"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NO_ACTIONABLE_DIRECTION = "NO_ACTIONABLE_DIRECTION"
    RISK_APPROVED = "RISK_APPROVED"
    RISK_REJECTED = "RISK_REJECTED"
    RISK_LIMIT_EXCEEDED = "RISK_LIMIT_EXCEEDED"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    RUNTIME_DEGRADED = "RUNTIME_DEGRADED"
    SHUTDOWN_REQUESTED = "SHUTDOWN_REQUESTED"
    MARKET_CLOSED = "MARKET_CLOSED"
    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"
    LIQUIDITY_INSUFFICIENT = "LIQUIDITY_INSUFFICIENT"
    DUPLICATE_EVENT = "DUPLICATE_EVENT"
    UNSUPPORTED_INSTRUMENT = "UNSUPPORTED_INSTRUMENT"
    ZERO_HALLUCINATION_VERIFIED = "ZERO_HALLUCINATION_VERIFIED"
    ZERO_HALLUCINATION_REJECTED = "ZERO_HALLUCINATION_REJECTED"
    PAPER_EXECUTION_FAILED = "PAPER_EXECUTION_FAILED"
    EXECUTION_INTENT_CREATED = "EXECUTION_INTENT_CREATED"
    NO_EXECUTION_INTENT = "NO_EXECUTION_INTENT"
    PAPER_TRADE_OPENED = "PAPER_TRADE_OPENED"
    INTERNAL_EXCEPTION = "INTERNAL_EXCEPTION"
    UNCLASSIFIED_REASON = "UNCLASSIFIED_REASON"


REASON_ALIASES = {
    "VERIFIED": PipelineReasonCode.ZERO_HALLUCINATION_VERIFIED,
    "MISSING_COMBINED_SIGNAL_DATA": PipelineReasonCode.INSUFFICIENT_EVIDENCE,
    "COMBINED_SIGNAL_CONFLICT": PipelineReasonCode.SIGNAL_CONFLICT,
    "SIGNALS_CONFLICT": PipelineReasonCode.SIGNAL_CONFLICT,
    "SIGNAL_CONFIDENCE_BELOW_THRESHOLD.": PipelineReasonCode.LOW_CONFIDENCE,
    "SIGNAL_CONFIDENCE_BELOW_THRESHOLD": PipelineReasonCode.LOW_CONFIDENCE,
    "NO_ACTIONABLE_DIRECTION.": PipelineReasonCode.NO_ACTIONABLE_DIRECTION,
    "NO_ACTIONABLE_DIRECTION": PipelineReasonCode.NO_ACTIONABLE_DIRECTION,
    "REQUIRED_DECISION_DATA_IS_MISSING.": PipelineReasonCode.INSUFFICIENT_EVIDENCE,
    "NO_EVIDENCE_WAS_PROVIDED.": PipelineReasonCode.NO_DATA,
    "NO_SIGNAL_ASSESSMENTS_WERE_PROVIDED.": PipelineReasonCode.NO_STRATEGY_SIGNALS,
    "DECISION_PROPOSAL_BASED_ON_ALIGNED_EVIDENCE.": PipelineReasonCode.OK,
}


def normalize_reason_code(value: str | PipelineReasonCode) -> PipelineReasonCode:
    if isinstance(value, PipelineReasonCode):
        return value
    normalized = value.strip().upper().replace(" ", "_").replace(";", "")
    return REASON_ALIASES.get(
        normalized,
        PipelineReasonCode.__members__.get(normalized, PipelineReasonCode.UNCLASSIFIED_REASON),
    )


@dataclass(frozen=True)
class PipelineStageResult:
    stage: str | PipelineStageName
    outcome: PipelineStageOutcome
    reason_code: str | PipelineReasonCode
    latency_ms: float
    missing_data: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        if isinstance(self.stage, PipelineStageName):
            object.__setattr__(self, "stage", self.stage.value)
        object.__setattr__(self, "reason_code", normalize_reason_code(self.reason_code).value)


class PipelineStageRecorder:
    def __init__(self, started_at: float | None = None) -> None:
        self.started_at = started_at if started_at is not None else perf_counter()
        self.results: list[dict[str, object]] = []

    def mark(
        self,
        stage: str | PipelineStageName,
        outcome: PipelineStageOutcome,
        reason_code: str | PipelineReasonCode,
        missing_data: list[str] | None = None,
        conflicts: list[str] | None = None,
    ) -> dict[str, object]:
        stage_name = stage.value if isinstance(stage, PipelineStageName) else stage
        result = asdict(
            PipelineStageResult(
                stage=stage_name,
                outcome=outcome,
                reason_code=reason_code,
                latency_ms=round((perf_counter() - self.started_at) * 1000, 4),
                missing_data=missing_data or [],
                conflicts=conflicts or [],
            )
        )
        self.results.append(result)
        return result
