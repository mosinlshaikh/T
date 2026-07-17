from dataclasses import asdict
from pathlib import Path

from trading_os.config import TradingOSConfig
from trading_os.market.timeframes import Timeframe
from trading_os.orchestrator import TradingOSBackend
from trading_os.pipeline.decision_to_trade import PipelineInput
from trading_os.pipeline.stage_result import (
    PipelineReasonCode,
    PipelineStageName,
    PipelineStageOutcome,
    PipelineStageRecorder,
    PipelineStageResult,
    normalize_reason_code,
)


def test_pipeline_stage_result_is_machine_readable() -> None:
    result = PipelineStageResult(
        stage="risk",
        outcome=PipelineStageOutcome.SKIP,
        reason_code="RISK_REJECTED",
        latency_ms=1.25,
        missing_data=["risk_context"],
        conflicts=["max_active_risk"],
    )

    payload = asdict(result)

    assert payload["stage"] == "risk"
    assert payload["outcome"] == PipelineStageOutcome.SKIP
    assert payload["reason_code"] == "RISK_REJECTED"
    assert payload["missing_data"] == ["risk_context"]
    assert payload["conflicts"] == ["max_active_risk"]
    assert "T" in payload["timestamp"]


def test_pipeline_stage_recorder_emits_ordered_stage_payloads() -> None:
    recorder = PipelineStageRecorder(started_at=0.0)
    first = recorder.mark(
        PipelineStageName.SHUTDOWN_GATE,
        PipelineStageOutcome.CONTINUE,
        PipelineReasonCode.OK,
    )
    second = recorder.mark(
        "risk",
        PipelineStageOutcome.SKIP,
        "RISK_REJECTED",
        conflicts=["max_active_risk"],
    )

    assert recorder.results == [first, second]
    assert first["stage"] == "shutdown_gate"
    assert first["reason_code"] == "OK"
    assert second["stage"] == "risk"
    assert second["reason_code"] == "RISK_REJECTED"
    assert second["conflicts"] == ["max_active_risk"]


def test_pipeline_reason_code_normalizes_known_decision_reasons() -> None:
    assert (
        normalize_reason_code("Signal confidence below threshold.")
        == PipelineReasonCode.LOW_CONFIDENCE
    )
    assert (
        normalize_reason_code("No actionable direction.")
        == PipelineReasonCode.NO_ACTIONABLE_DIRECTION
    )
    assert normalize_reason_code("Signals conflict") == PipelineReasonCode.SIGNAL_CONFLICT
    assert normalize_reason_code("unexpected custom text") == PipelineReasonCode.UNCLASSIFIED_REASON


class BrokenRiskEngine:
    def evaluate(self, _context: object) -> object:
        raise RuntimeError("boom")


def test_pipeline_internal_exception_fails_closed_to_skip(tmp_path: Path) -> None:
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(tmp_path / "audit.jsonl"),
        )
    )
    backend.decision_to_trade_pipeline.risk_engine = BrokenRiskEngine()  # type: ignore[assignment]

    result = backend.decision_to_trade_pipeline.run(
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

    assert result.status == "SKIP"
    assert result.decision.action.value == "SKIP"
    assert result.execution_intent is None
    assert result.paper_fill is None
    assert result.stage_results[-1]["reason_code"] == PipelineReasonCode.INTERNAL_EXCEPTION.value
