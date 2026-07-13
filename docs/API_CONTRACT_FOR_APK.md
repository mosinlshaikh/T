# API Contract for Future Android APK

This document describes the Phase 6 backend API contract for the future Android APK.

Architect attribution: **MOSIN LIYAKAT SHAIKH** designed the TTRL backend/API
contract direction for T TECHNOLOGY RESEARCH LAB. The product identity is
broader than Binance: **TTRL AI Trading OS / T Financial Intelligence OS**.

No APK is built in this phase. The API layer is a backend skeleton for dashboard, control, status, portfolio, trades, decisions, logs, and settings.

Canonical backend: `trading_os.api.app:app`. The `backend/` folder is
experimental and is not the Android integration target.

```text
Live trading: disabled
Real Binance order placement: absent/blocked
Withdrawals: never supported
Margin/futures: not supported
Architecture: Binance Spot only
Default mode: paper
```

## Response Standard

Every route returns:

```json
{
  "success": true,
  "message": "ok",
  "data": {},
  "timestamp": "2026-07-02T00:00:00+00:00",
  "request_id": "uuid",
  "warnings": [],
  "errors": []
}
```

Errors use safe messages. Stack traces and secrets are not returned.

## License Activation Endpoints

TTRL app license keys control app/backend access. They are not Binance API keys.
Binance API keys must still be created inside Binance and configured separately
through the backend/vault process.

Admin routes:

- `POST /admin/licenses/generate`
- `GET /admin/licenses`
- `GET /admin/licenses/{license_id}`
- `POST /admin/licenses/{license_id}/disable`
- `POST /admin/licenses/{license_id}/revoke`
- `POST /admin/licenses/{license_id}/suspend`
- `POST /admin/licenses/{license_id}/activate`

Client route:

- `POST /license/validate`

Example validation request:

```json
{
  "license_key": "TTRL-XXXX-XXXX-XXXX-XXXX",
  "package_name": "com.ttechnologyresearchlab.tradingos"
}
```

Admin generation requires `TTRL_ADMIN_TOKEN`. If the token is missing, admin
routes return `ADMIN_AUTH_NOT_CONFIGURED`. The full key is returned only once at
creation and persisted only as a hash.

The Android app calls only `/license/validate`. It does not include admin
generation routes, Binance credentials, or direct Binance execution.

## Status Endpoints

- `GET /status/bot`
- `GET /status/health`
- `GET /status/binance-readiness`
- `GET /status/shutdown`
- `GET /status/runtime`
- `GET /status/real-world-readiness`

Example:

```json
{
  "success": true,
  "message": "Runtime status loaded.",
  "data": {
    "bot_state": "PAPER_READY",
    "trading_mode": "paper",
    "live_trading_enabled": false,
    "api_readiness_status": "READY_FOR_PAPER",
    "supervisor_health": false
  }
}
```

Vault status reports availability only. It never returns API keys or secrets.

`/status/real-world-readiness` reports paper readiness, local AI evidence
readiness, risk guard status, kill-switch state, and live-execution blockers.
It must return `ready_for_real_money=false` and
`live_execution_available=false` in this build.

## Control Endpoints

- `POST /control/start`
- `POST /control/stop-graceful`
- `POST /control/emergency-stop`
- `POST /control/restart-runtime`
- `POST /control/pause-new-trades`
- `POST /control/resume-paper-trades`

There is no live mode endpoint.

Graceful shutdown:

- blocks new trades
- keeps active paper trades managed
- preserves stop-loss and take-profit behavior
- stops only after active state is safe

Emergency stop:

- activates kill switch
- blocks new trades immediately
- moves runtime state to `EMERGENCY_STOPPED`

## Portfolio Endpoints

- `GET /portfolio/summary`
- `GET /portfolio/wallet`
- `GET /portfolio/open-positions`
- `GET /portfolio/closed-positions`
- `GET /portfolio/pnl`
- `GET /portfolio/exposure`

The portfolio routes use the paper portfolio state manager. They do not fetch real Binance balances.

When database records exist, portfolio routes prefer persisted paper snapshots and positions. If persistence is empty, routes fall back to in-memory paper state.

## Trade Endpoints

- `GET /trades/open`
- `GET /trades/closed`
- `GET /trades/journal`
- `GET /trades/{trade_id}`
- `GET /trades/latest`

All trade data is paper/simulated by default.

Trade routes read persisted paper journal and position records when available.

## Decision Endpoints

- `GET /decisions/latest`
- `GET /decisions/history`
- `GET /decisions/{decision_id}`
- `GET /decisions/skipped`
- `GET /decisions/blocked`

Decision responses include:

- action: `BUY`, `SELL`, `HOLD`, or `SKIP`
- confidence
- evidence
- reason
- missing data
- conflicts
- zero-hallucination verification status
- risk approval/rejection status

Decision routes read persisted AI decisions when available, then fall back to audit history.

## Audit Endpoints

- `GET /audit/latest`
- `GET /audit/events`
- `GET /audit/errors`
- `GET /audit/security`
- `GET /audit/runtime`

Audit responses are redacted. Secret-like fields are never returned.

Audit routes read persisted audit events when available.

## Settings Endpoints

- `GET /settings/risk`
- `PUT /settings/risk`
- `GET /settings/strategy`
- `PUT /settings/strategy`
- `GET /settings/security`
- `GET /settings/notifications`
- `PUT /settings/notifications`

Risk settings enforce safe limits. Stop-loss and take-profit remain required.

Settings updates are persisted locally and continue to enforce paper mode, live trading disabled, withdrawals disabled, and margin/futures disabled.

Security settings cannot:

- enable live trading
- enable withdrawals
- submit API keys

API key submission endpoints are intentionally not added in Phase 6.

## Report Endpoints

- `GET /reports/daily`
- `GET /reports/weekly`
- `GET /reports/monthly`
- `GET /reports/performance`
- `GET /reports/risk`
- `GET /reports/hallucination`
- `GET /reports/skipped-trades`
- `GET /reports/strategies`
- `GET /reports/runtime`

Reports use persisted paper-mode data only. If history is missing, the API returns `unknown`, `insufficient_data`, or `NOT_ENOUGH_HISTORY` instead of inventing outcomes.

## Local AI Learning Endpoints

These routes expose the internal paper-only learning engine. They do not use an
external AI API key and do not change live trading behavior.

- `GET /learning/local-ai`
- `GET /learning/market-king-score`
- `GET /learning/recommendations`

Rules:

- uses persisted paper evidence only
- returns `insufficient_data` when evidence is missing
- advisory only
- no automatic strategy changes
- no live trading impact
- no profit guarantee language

## Dashboard Data Contracts

The backend includes response contracts for performance cards, PnL chart data, strategy score cards, risk summary cards, decision/trade/audit/shutdown timelines, and safety score.

## Android Phase 9 Source Scaffold

Android source is located at:

```text
android_app/
```

The APK source uses the API contract as a control panel and dashboard only. It must not contain Binance credentials and must not execute Binance orders directly.

Screens scaffolded:

- Splash / Boot
- Dashboard
- Market Intelligence
- Trade Control
- Portfolio
- Decisions
- Trade Journal
- Reports
- Settings
- Audit / Safety

## Phase 10 Readiness Notes

The backend and Android client method names have been reviewed against this contract. The Android app remains source-only until the explicit final APK build command.

Release blockers before APK generation:

- no APK/AAB build has been run
- no app signing/release packaging has been done
- live trading remains disabled
- credential submission remains unavailable
- withdrawals remain unsupported

## Phase 9B UI Contract Additions

The Android source now includes:

- English/Hinglish language selector
- API Setup Wizard
- Bot Brain explanation screen
- Safety Lock screen
- App Lock / Unlock scaffold
- Onboarding flow
- Release Readiness screen
- Offline backend banner with connected/disconnected/degraded/unknown states

These additions are UI/control scaffolds only. They do not add credential submission, live trading, withdrawals, or direct Binance order placement.

## APK Integration Plan

Future APK screens can map directly to:

- Dashboard: `/status/health`, `/portfolio/summary`
- Runtime control: `/control/*`
- Portfolio: `/portfolio/*`
- Trade journal: `/trades/*`
- AI decisions: `/decisions/*`
- Audit/logs: `/audit/*`
- Settings: `/settings/*`

The APK must treat `live_trading_enabled=false` as a hard invariant.

## Security Rules

- Do not send real Binance credentials through this API.
- Do not display secrets in APK screens.
- Do not store secrets in APK logs.
- Do not add withdrawal support.
- Do not add margin/futures execution.
- Do not add a live trading toggle.

Evidence-first and zero-hallucination rules remain active for all trading decisions.
