from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PipelineStageOutcome(str, Enum):
    CONTINUE = "CONTINUE"
    HOLD = "HOLD"
    SKIP = "SKIP"
    REJECT = "REJECT"
    APPROVE_PROPOSAL = "APPROVE_PROPOSAL"


@dataclass(frozen=True)
class PipelineStageResult:
    stage: str
    outcome: PipelineStageOutcome
    reason_code: str
    latency_ms: float
    missing_data: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
