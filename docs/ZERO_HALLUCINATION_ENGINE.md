# Zero Hallucination Engine

Module:

```text
trading_os/ai/verified_decision_engine.py
trading_os/ai/decision_brain.py
```

`backend/app/decision/zero_hallucination_engine.py` is experimental and is not
the final integration target.

Rules:

- No Data = No Trade.
- No Proof = No Decision.
- Missing candle data returns `SKIP`.
- Unstable Binance connection returns `SKIP`.
- Conflicting signals return `SKIP` or `HOLD`.
- Every decision requires evidence.
- No fake whale claims.
- No fake news claims.
- No guaranteed profit language.
- No assumed market movement.

Every decision must include timestamp, symbol, price, evidence snapshot, confidence score, final decision, and reason.
