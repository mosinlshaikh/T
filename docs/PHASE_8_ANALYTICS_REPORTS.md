# Phase 8 Strategy Learning, Analytics, Reports, and Decision Review

Phase 8 adds evidence-based analytics and reporting over persisted paper-mode data.

This phase does not build an APK, does not build an EXE, does not enable live trading, and does not place real Binance orders.

```text
Data source: persisted paper-mode records
Live trading: disabled
Withdrawals: forbidden
Margin/futures: not supported
Architecture: Binance Spot only
```

## Strategy Performance Analyzer

Module:

```text
trading_os/analytics/strategy_performance.py
```

It analyzes persisted paper data for:

- total signals per strategy
- `BUY`, `SELL`, `HOLD`, `SKIP` counts
- paper trade count
- win/loss count
- win rate
- realized and unrealized PnL
- average PnL
- max drawdown
- risk rejection count
- hallucination block count
- confidence versus outcome summary

If data is missing, the report returns `insufficient_data` or `unknown`.

## Decision Review Engine

Module:

```text
trading_os/analytics/decision_review.py
```

Decision review outputs:

- `GOOD_DECISION`
- `BAD_DECISION`
- `INCOMPLETE_DATA`
- `RISK_BLOCKED`
- `HALLUCINATION_BLOCKED`
- `NOT_ENOUGH_HISTORY`

The engine reviews only persisted evidence, missing data, conflicts, zero-hallucination status, risk result, execution intent availability, and paper outcome when available.

## Learning Feedback Engine

Module:

```text
trading_os/learning/feedback_engine.py
```

Feedback is advisory only. It can summarize:

- which signals worked
- which signals failed
- which signals were blocked
- strategies needing more data
- confidence ranges
- skip conditions
- risk rules that blocked unsafe trades

It does not auto-change strategy rules and has no live trading impact.

## Report Generator

Module:

```text
trading_os/reports/generator.py
```

Reports:

- daily report
- weekly report skeleton
- monthly report skeleton
- latest performance snapshot
- risk report
- hallucination safety report
- skipped trade report
- strategy comparison report
- shutdown/runtime report

Reports are dict/JSON-compatible. A markdown export helper is included.

## APK Report API Endpoints

Routes:

- `GET /reports/daily`
- `GET /reports/weekly`
- `GET /reports/monthly`
- `GET /reports/performance`
- `GET /reports/risk`
- `GET /reports/hallucination`
- `GET /reports/skipped-trades`
- `GET /reports/strategies`
- `GET /reports/runtime`

All responses use the shared API response format and return paper data only.

## Dashboard Data Contracts

Module:

```text
trading_os/api/dashboard_models.py
```

Backend response models are prepared for:

- performance cards
- PnL chart data
- strategy score cards
- risk summary cards
- decision timeline
- trade timeline
- audit timeline
- shutdown timeline
- safety score

These are response contracts only, not APK UI implementation.

## Safety Score Engine

Module:

```text
trading_os/analytics/safety_score.py
```

The safety score uses:

- live trading disabled
- withdrawals unsupported
- zero-hallucination blocks
- risk rejections
- missing-data skips
- emergency stop status
- API vault status
- evidence quality

Output:

- score `0-100`
- level: `SAFE`, `CAUTION`, `DANGER`, or `UNKNOWN`
- reasons
- recommended action

## Safety Invariants

- Live trading remains impossible by default.
- Real order placement remains absent and blocked.
- No withdrawals.
- No margin/futures execution.
- Spot-only architecture.
- Evidence-first and zero-hallucination rules remain active.
- No market fact is invented when data is missing.
- No profit guarantee language is produced.
