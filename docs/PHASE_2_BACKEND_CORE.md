# Phase 2 Backend Core

This phase extends the AI Binance Trading OS backend foundation. It still does not build an APK, EXE, or live trading system.

```text
Default mode: paper/sandbox
Live trading: disabled
Withdraw permission: forbidden
Real API keys in repo: forbidden
```

## Phase 2 Modules

| Area | Module | Purpose |
| --- | --- | --- |
| Binance knowledge | `trading_os/binance/spot_knowledge.py` | Symbol rules, precision, min notional, trading status, rate-limit plan |
| REST connector | `trading_os/connectors/rest_api.py` | Public/private request design; private disabled by default |
| WebSocket connector | `trading_os/connectors/websocket_market_data.py` | Live ticker and market stream skeletons |
| Market data | `trading_os/market/market_data_engine.py` | REST snapshot request, tick/snapshot ingestion, candle requests |
| Candles | `trading_os/market/candle_engine.py` | Candle collector with `1m`, `5m`, `15m`, `1h`, `4h` support |
| Order book | `trading_os/market/order_book_engine.py` | Snapshot model and spread calculation |
| Volume spikes | `VolumeSpikeDetector` | Volume spike detector skeleton |
| AI brain v1 | `trading_os/ai/decision_brain.py` | Evidence-bound BUY/SELL/HOLD/SKIP proposal builder |
| Zero hallucination | `trading_os/ai/verified_decision_engine.py` | Verifies evidence, source, timestamp, and unsupported claims |
| Risk v1 | `trading_os/risk/risk_engine.py` | Reserve, exposure, loss, cooldown, SL/TP, kill-switch checks |
| Shutdown | `trading_os/runtime/shutdown_engine.py` | Professional shutdown state machine |
| Audit | `trading_os/audit/audit_logger.py` | Required event logging methods |

## AI Decision Rules

Decision output is limited to:

- `BUY`
- `SELL`
- `HOLD`
- `SKIP`

Every decision proposal includes:

- `confidence`
- `evidence`
- `reason`
- `missing_data`
- `conflict_signals`
- `timestamp`
- `symbol`
- `timeframe`

Rules:

- No evidence means `SKIP`.
- Missing required data means `SKIP`.
- Conflicting signals mean `HOLD` or `SKIP`.
- Profit guarantees are rejected.
- Whale, news, candle, or order-book claims require matching evidence types.

## Zero Hallucination Rules

The verified decision engine checks:

- evidence exists
- evidence has source and timestamp
- signals have source and timestamp
- required evidence is present
- unsupported claim language is absent
- domain claims are backed by matching evidence

Each verified result includes:

- `verified_decision=true/false`
- `rejection_reason` when blocked

## Required Evidence

The current default required evidence is:

- `market_tick`
- `risk_check`
- `capital_check`

Additional domain claims require additional evidence:

- whale claim -> `whale_signal`
- news claim -> `news_signal`
- candle claim -> `candle`
- order book claim -> `order_book`

## Risk Engine v1 Rules

Risk Engine v1 enforces:

- 10% reserve capital lock
- 5% max risk exposure rule
- max trade size
- daily loss limit
- consecutive loss limit
- cooldown after loss
- stop-loss required
- take-profit required
- emergency kill switch check

The engine returns a rejection list instead of silently approving unsafe intent.

## Smart Shutdown Behavior

Shutdown states:

- `RUNNING`
- `SHUTDOWN_REQUESTED`
- `FINISHING_ACTIVE_TRADES`
- `SAVING_LOGS`
- `SAFELY_STOPPED`
- `EMERGENCY_STOPPED`

Behavior:

- When the user turns the bot OFF, no new trades are accepted.
- Active/open trades continue to be managed.
- Stop-loss and take-profit must remain active.
- The backend stops only after active trade state is safe and logs are saved.
- Emergency stop halts immediately and marks the state as `EMERGENCY_STOPPED`.

## Audit Logger Events

The audit logger has explicit methods for:

- market snapshot
- signal
- AI decision
- skipped trade reason
- blocked hallucination
- risk rejection
- order intent
- shutdown state change

## Live Trading Boundary

Phase 2 still does not enable live trading. `BinanceSpotConnector.execute_order()` remains disabled.

Before any future live phase:

- secrets must live outside git
- Binance keys must not have withdraw permission
- paper-mode integration tests must exist
- risk and shutdown engines must be enforced
- audit logs must be mandatory
- user opt-in must be explicit
