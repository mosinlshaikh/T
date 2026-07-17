# Decision Pipeline Stage Results

The paper decision pipeline now records machine-readable stage results for each
decision-to-trade run.

This is paper/audit monitoring only. It does not enable live trading and does
not send private Binance orders.

## Stage Result Shape

Each stage result contains:

- `stage`
- `outcome`
- `reason_code`
- `latency_ms`
- `missing_data`
- `conflicts`
- `timestamp`

`reason_code` is normalized through `trading_os.pipeline.stage_result.PipelineReasonCode`.
Unknown ad-hoc text is not treated as success; it becomes `UNCLASSIFIED_REASON`
until mapped to an approved stable code.

Stage recording is handled by `PipelineStageRecorder`, exported from
`trading_os.pipeline`. It preserves insertion order, stage latency, missing-data
lists, conflict lists, and normalized reason codes.

Valid outcomes are:

- `CONTINUE`
- `HOLD`
- `SKIP`
- `REJECT`
- `APPROVE_PROPOSAL`

## Current Stages

- `shutdown_gate` - implemented by `ShutdownGateStage`
- `market_intelligence` - implemented by `MarketIntelligenceStage`
- `combined_signal` - implemented by `SignalCombinationStage`
- `strategy_signal` - implemented by `StrategySignalStage`
- `risk` - implemented by `RiskAssessmentStage`
- `ai_decision` - implemented by `DecisionVerificationStage`
- `zero_hallucination` - implemented by `DecisionVerificationStage`
- `trade_lifecycle` - implemented by `TradeExecutionStage`
- `execution_intent` - implemented by `TradeExecutionStage`
- `paper_execution` - implemented by `TradeExecutionStage`
- `pipeline_exception`

`pipeline_exception` is emitted only when an internal exception escapes the
decision path. The pipeline fails closed to `SKIP`, creates no execution intent,
opens no paper fill, and records `INTERNAL_EXCEPTION`.

Audit payload formatting is centralized through `PipelineAuditAdapter`. The
adapter writes the same audit events as before, but keeps payload construction
outside the orchestration path.

## Stable Reason Codes

Current canonical reason codes include:

- `OK`
- `NO_DATA`
- `STALE_DATA`
- `INVALID_SCHEMA`
- `TIMESTAMP_GAP`
- `INSUFFICIENT_EVIDENCE`
- `NO_COMBINER_CONFIGURED`
- `NO_INTELLIGENCE_SIGNALS`
- `NO_STRATEGY_SIGNALS`
- `SIGNAL_CONFLICT`
- `LOW_CONFIDENCE`
- `NO_ACTIONABLE_DIRECTION`
- `RISK_APPROVED`
- `RISK_REJECTED`
- `RISK_LIMIT_EXCEEDED`
- `KILL_SWITCH_ACTIVE`
- `RUNTIME_DEGRADED`
- `SHUTDOWN_REQUESTED`
- `MARKET_CLOSED`
- `SPREAD_TOO_WIDE`
- `LIQUIDITY_INSUFFICIENT`
- `DUPLICATE_EVENT`
- `UNSUPPORTED_INSTRUMENT`
- `ZERO_HALLUCINATION_VERIFIED`
- `ZERO_HALLUCINATION_REJECTED`
- `PAPER_EXECUTION_FAILED`
- `EXECUTION_INTENT_CREATED`
- `NO_EXECUTION_INTENT`
- `PAPER_TRADE_OPENED`
- `INTERNAL_EXCEPTION`
- `UNCLASSIFIED_REASON`

## APK Monitoring

The monitor API exposes recent pipeline stages on paper scan history rows under:

```text
GET /monitor/paper-scan-history
```

Each row may include:

```json
{
  "pipeline_stages": [
    {
      "stage": "risk",
      "outcome": "CONTINUE",
      "reason_code": "RISK_APPROVED",
      "latency_ms": 4.21,
      "missing_data": [],
      "conflicts": []
    }
  ]
}
```

The Android dashboard renders these rows as the Decision Pipeline section so the
user can see why a paper scan became `BUY`, `SELL`, `HOLD`, or `SKIP`.

## Safety Rules

- Missing required data remains `SKIP`.
- Conflict-heavy signals remain `HOLD` or `SKIP`.
- Zero-hallucination rejection remains blocked.
- Risk rejection remains blocked.
- Internal exceptions fail closed to `SKIP`.
- Live trading remains disabled.
