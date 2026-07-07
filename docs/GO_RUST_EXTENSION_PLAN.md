# Go and Rust Extension Layer

This repository now includes safe Go and Rust scaffolds for future high-performance
support tools.

## Scope

- Python remains the canonical backend in `trading_os/`.
- Go is used for lightweight operational probes.
- Rust is used for local safety guard checks.
- Neither Go nor Rust executes Binance orders.
- Neither Go nor Rust stores API keys, secrets, or withdrawal permissions.

## Added Components

```text
go_services/market_probe/
  main.go      # checks the backend /monitor/paper-live endpoint

rust_services/safety_guard/
  src/main.rs  # blocks unsafe env flags before automation
```

## Paper Auto Trader

The backend now has a paper-only auto trader:

```text
trading_os/runtime/paper_auto_trader.py
```

API endpoints:

- `POST /control/paper-auto-trader/tick`
- `POST /control/paper-auto-trader/start`
- `POST /control/paper-auto-trader/stop`
- `GET /control/paper-auto-trader/status`

The loop reads public market data, runs the existing evidence-first pipeline,
updates paper portfolio/journal/audit state, and refuses live trading.

## Safety Boundary

Live trading remains disabled:

```text
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
MANUAL_LIVE_UNLOCK=false
BINANCE_WITHDRAWALS_SUPPORTED=false
```

Real-money execution must stay out of this public phase. A future private and
audited live phase would need exchange sandbox tests, manual approvals, separate
secrets management, legal/compliance review, and kill-switch drills.
