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

Valid outcomes are:

- `CONTINUE`
- `HOLD`
- `SKIP`
- `REJECT`
- `APPROVE_PROPOSAL`

## Current Stages

- `shutdown_gate`
- `market_intelligence`
- `combined_signal`
- `strategy_signal`
- `risk`
- `ai_decision`
- `zero_hallucination`

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
- Live trading remains disabled.
