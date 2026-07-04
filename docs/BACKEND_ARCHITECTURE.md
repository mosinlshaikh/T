# Backend Architecture

The canonical backend foundation lives in:

```text
trading_os/
```

`trading_os/` is the source of truth for final pre-APK testing, API contracts,
runtime supervision, persistence, paper trading, reporting, licensing, and
Android integration.

The `backend/` folder is retained only as an experimental scaffold from an
earlier folder-layout phase. It is not the active runtime target.

## Safety Defaults

```text
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
MANUAL_LIVE_UNLOCK=false
BINANCE_WITHDRAWALS_SUPPORTED=false
```

The backend is Binance Spot only. Margin, futures, portfolio margin, withdrawals, internal transfer, universal transfer, prediction trading, and copy trading are not implemented.

## Runtime Boundary

APK:

- dashboard
- control panel
- alerts
- reports
- settings

Backend:

- AI decision brain
- Binance Spot connector skeleton
- risk engine
- order intent validation
- paper/sandbox execution
- runtime monitoring

Live execution remains disabled until a future audited phase.

## Package Layout

The canonical backend contains modules for Binance rules, market engines,
intelligence, strategies, decisions, risk, execution, security, database, audit,
API routes, monitoring, licensing, and bot modes.

Every decision must be evidence-first. Missing data returns `SKIP`.
