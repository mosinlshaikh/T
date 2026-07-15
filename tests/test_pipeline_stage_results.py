from dataclasses import asdict

from trading_os.pipeline.stage_result import PipelineStageOutcome, PipelineStageResult


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
