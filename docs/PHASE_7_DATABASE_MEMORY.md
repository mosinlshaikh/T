# Phase 7 Database Persistence, Memory System, and Durable Bot State

Phase 7 adds local persistence and evidence-based memory for the AI Binance Trading OS backend.

This phase does not build an APK, does not build an EXE, does not enable live trading, and does not place real Binance orders.

```text
Default persistence: SQLite
Default database: data/trading_os.sqlite3
Live trading: disabled
Withdrawals: forbidden
Margin/futures: not supported
Architecture: Binance Spot only
```

## Database Layer

Modules:

```text
trading_os/db/models.py
trading_os/db/storage.py
trading_os/db/repository.py
trading_os/db/migrations.py
```

The first persistence implementation uses SQLite from the Python standard library. The database path is configurable through `TradingOSConfig.database_url`.

The repository stores JSON payload records by category. This keeps Phase 7 flexible while the backend architecture is still evolving.

Secrets are redacted before persistence. API keys and API secrets are not stored.

## Durable Records

The repository supports durable records for:

- bot runtime state
- portfolio snapshots
- open positions
- closed positions
- trade journal entries
- execution intents
- AI decisions
- strategy signals
- market intelligence snapshots
- risk approvals/rejections
- zero-hallucination verification results
- audit events
- notification events
- user/app settings
- shutdown state
- daily performance summary

## Repository Methods

Implemented methods include:

- `save_bot_state`
- `get_latest_bot_state`
- `save_portfolio_snapshot`
- `get_latest_portfolio_snapshot`
- `save_open_position`
- `update_open_position`
- `close_position`
- `save_trade_journal_entry`
- `list_trade_journal`
- `save_ai_decision`
- `list_ai_decisions`
- `save_audit_event`
- `list_audit_events`
- `save_settings`
- `get_settings`
- `save_daily_performance`
- `get_daily_performance`

## Bot Memory

Module:

```text
trading_os/memory/bot_memory.py
```

The memory system summarizes persisted evidence only:

- last decisions
- recent skipped trades
- recent risk rejections
- recent hallucination blocks
- recent winning/losing paper trades
- daily PnL memory
- market condition history summary
- strategy performance memory

If data is missing, memory reports missing or unknown. It does not invent market facts and does not produce profit guarantees.

## Runtime Restore

The runtime supervisor can load the latest persisted bot state during boot.

Restore behavior:

- previous emergency stop keeps the bot stopped until manual review
- interrupted or active paper state moves runtime into a safe degraded state
- normal paper state can boot through config, vault, and API readiness checks

Open position persistence is available for future deeper resume behavior.

## API Integration

Phase 6 API routes now prefer persisted data where available:

- status
- portfolio
- trades
- decisions
- audit
- settings

If the database is empty, routes fall back to in-memory/default backend state.

## Settings Persistence

Persisted settings include:

- risk settings
- strategy settings
- notification settings
- security placeholders

Validation keeps safety invariants:

- live trading cannot be enabled
- withdrawals cannot be enabled
- margin/futures cannot be enabled
- risk settings remain inside safe limits

## Audit Persistence

The audit logger writes JSONL logs and can also persist each audit event to SQLite through the repository.

Sensitive fields are redacted before database storage.

## Daily Performance Summary

Module:

```text
trading_os/db/performance.py
```

The summary includes:

- date
- paper starting balance
- ending balance
- realized PnL
- unrealized PnL
- number of decisions
- number of skipped trades
- number of risk rejections
- number of hallucination blocks
- number of paper trades
- win/loss count
- drawdown

## Safety Invariants

- Live trading remains impossible by default.
- Real order placement remains absent and blocked.
- No withdrawals.
- No margin/futures execution.
- Spot-only architecture.
- Evidence-first and zero-hallucination rules remain active.
- Secrets are not stored in the database, logs, docs, or tests.
