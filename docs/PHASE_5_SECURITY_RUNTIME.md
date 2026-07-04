# Phase 5 Security, API Vault, Runtime Supervisor, and 24x7 Backend Service

Phase 5 adds the safe runtime foundation for operating the AI Binance Trading OS backend as a supervised paper/sandbox service.

This phase does not build an APK, does not build an EXE, does not enable live trading, and does not place real Binance orders.

```text
Default mode: paper
Live trading: disabled
Withdraw logic: forbidden
Margin/futures execution: not supported
Architecture: Binance Spot only
```

## Secure Configuration System

Module:

```text
trading_os/config.py
```

The configuration layer supports:

- simple `.env` loading
- required safety validation
- safe defaults
- config redaction for logs
- health reports without secrets

Safe defaults:

```text
LIVE_TRADING_ENABLED=false
TRADING_MODE=paper
BINANCE_WITHDRAWALS_SUPPORTED=false
```

`.env` remains gitignored. `.env.example` contains placeholders only.

## API Vault Design

Module:

```text
trading_os/security/api_key_vault.py
```

The vault design exposes provider interfaces only:

- `ENV_PROVIDER`
- `LOCAL_VAULT_PROVIDER`
- `CLOUD_SECRET_PROVIDER`

Current behavior checks credential availability only. It never prints, logs, stores, or returns raw secrets.

Permission expectation:

```text
reading=true
spot_trading=optional/future
withdrawals=false
```

Withdraw permission remains forbidden.

## Binance API Permission Verifier

Module:

```text
trading_os/security/permission_verifier.py
```

The verifier checks safe metadata and returns:

- `READY_FOR_PAPER`
- `READY_FOR_SANDBOX`
- `LIVE_BLOCKED`
- `MISCONFIGURED`
- `SECRET_MISSING`

It detects:

- missing read permission
- live mode blocked by default
- withdraw permission misconfiguration
- missing sandbox credential pair

No API key value or API secret value is exposed.

## Runtime Supervisor

Module:

```text
trading_os/runtime/supervisor.py
```

The supervisor provides:

- 24x7 loop skeleton
- heartbeat
- graceful start/stop
- crash guard
- auto-reconnect skeleton
- retry with backoff
- network failure state
- Binance connection failure state
- shutdown coordination with `SmartShutdownEngine`

When unhealthy, it blocks trade execution. Live trading is still impossible because execution modules only create paper-safe intents.

## Bot State Machine

Module:

```text
trading_os/runtime/bot_state.py
```

States:

- `BOOTING`
- `CONFIG_CHECK`
- `VAULT_CHECK`
- `API_PERMISSION_CHECK`
- `PAPER_READY`
- `SANDBOX_READY`
- `LIVE_BLOCKED`
- `RUNNING`
- `DEGRADED`
- `SHUTDOWN_REQUESTED`
- `SAFELY_STOPPED`
- `EMERGENCY_STOPPED`
- `ERROR`

## Notification Engine Skeleton

Module:

```text
trading_os/notifications/engine.py
```

Adapters:

- Telegram placeholder
- WhatsApp placeholder
- Email placeholder

Event types:

- `BOT_STARTED`
- `BOT_STOPPED`
- `TRADE_SIGNAL`
- `TRADE_SKIPPED`
- `RISK_REJECTED`
- `HALLUCINATION_BLOCKED`
- `SHUTDOWN_REQUESTED`
- `EMERGENCY_STOPPED`
- `ERROR`

Notification payload metadata is sanitized so credentials are not sent in messages.

## Health API Models

Module:

```text
trading_os/api/health_models.py
```

Prepared backend response models include:

- bot status
- config status
- vault status
- Binance readiness status
- portfolio summary
- latest decisions
- latest audit events
- shutdown status

These are models only. No APK API server is built in this phase.

## Audit Events

The audit logger now records:

- config validation result
- secret availability status only
- API readiness result
- runtime heartbeat
- supervisor state changes
- reconnect attempts
- notification dispatch result
- health snapshot

Audit records must never include raw credentials.

## Safety Invariants

- Live trading remains impossible by default.
- Real Binance order placement remains absent and blocked.
- No withdrawal support exists.
- No margin or futures execution exists.
- Binance Spot remains the architecture boundary.
- Evidence-first and zero-hallucination rules remain active.
