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
- `POST /control/paper-auto-trader/scan-radar`
- `POST /control/paper-session/start`
- `POST /control/paper-session/stop`
- `GET /control/paper-session/status`
- `POST /control/manual-paper-demo/open`
- `POST /control/manual-paper-demo/close-market`
- `POST /control/manual-paper-demo/simulate-stop-loss`
- `POST /control/manual-paper-demo/simulate-take-profit`

There is no live mode endpoint.

Paper session endpoints run repeated public-market paper scans for learning and
monitoring. They do not place real Binance orders and cannot enable live
trading.

`/control/paper-auto-trader/scan-radar` uses the public Market Radar shortlist
as the input symbols for a deep paper scan. It remains paper-only and cannot
send real Binance orders.

`/control/manual-paper-demo/open` opens a capped paper-only walkthrough position
using public ticker data. It is clearly labeled `MANUAL PAPER DEMO`; it is not
an AI decision and never sends a real Binance order.

The manual paper demo close, stop-loss, and take-profit endpoints complete the
paper lifecycle for APK testing. They only affect paper simulator state and do
not call private Binance APIs.

## Monitor Endpoints

- `GET /monitor/paper-live`
- `GET /monitor/market-evidence`
- `GET /monitor/candle-detail?symbol=BTCUSDT&timeframe=5m&limit=40`
- `GET /monitor/paper-scan-summary`
- `GET /monitor/paper-scan-history`
- `GET /monitor/strategy-blockers`
- `GET /monitor/market-radar`
- `GET /monitor/fast-market-state`
- `GET /monitor/paper-demo-readiness`

`/monitor/paper-live` is the main APK dashboard feed for public market data,
paper-only decisions, paper positions, paper journal, and audit timeline.

`/monitor/market-evidence` returns the latest candle, order book, whale, news,
market structure, conflict, and missing-data evidence rows for APK display. It
is evidence-only and returns `live_trading_enabled=false`.

`/monitor/candle-detail` returns chart-ready OHLC candle rows plus trend, range,
volume, and missing-data status for APK display. If candle data is unavailable,
the response keeps `missing_data=["candles"]` and the decision rule remains
`Missing candle data = SKIP`.

`/monitor/paper-scan-summary` returns the latest public-data paper scan result:
symbol, action, confidence, why no trade was opened, paper fill ID when present,
and safety flags.

`/monitor/paper-scan-history` returns audit-derived paper scan rows. Rows include
`strategy_breakdown` and `pipeline_stages` so the APK can show exactly which
pipeline gates continued, held, skipped, or rejected a paper trade candidate.

`/monitor/strategy-blockers` summarizes recent HOLD/SKIP reasons, pipeline
blockers, low-confidence counts, and symbol frequency. It is advisory only and
does not auto-change strategy thresholds.

`/monitor/market-radar` performs a public-data, all-USDT 24h ticker pre-filter.
It ranks candidates by volume, absolute movement, volatility, and trade
activity, then returns a deep-scan shortlist. It does not place orders.

`/monitor/fast-market-state` returns the in-memory public ticker cache used for
low-latency prefiltering. If the cache is empty, the backend may seed it from a
public Binance 24h ticker REST snapshot. The route remains public-data-only and
does not place orders. Deep candle, order book, news, whale, risk, and
zero-hallucination checks still run before any paper trade intent.

When the FastAPI backend starts, it can run a public Binance miniTicker
WebSocket task to refresh the same cache continuously. Set
`T_MARKET_STREAM_ENABLED=false` to disable that background public-data stream.
The stream never reads API keys and never sends orders.

`/monitor/paper-demo-readiness` returns computed readiness percentages for the
paper backend/APK monitoring contract and paper demo contract. It must always
return `real_money_ready=false` in this build.

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
- `GET /settings/strategy-catalog`
- `GET /settings/security`
- `GET /settings/notifications`
- `PUT /settings/notifications`

Risk settings enforce safe limits. Stop-loss and take-profit remain required.

Settings updates are persisted locally and continue to enforce paper mode, live trading disabled, withdrawals disabled, and margin/futures disabled.

`/settings/strategy-catalog` returns the Binance Spot paper strategy ecosystem:
candle/structure, order book, volume, whale, news, risk, local AI, and master
combiner modules. It is advisory only and does not enable live execution.

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
- `GET /reports/dashboard-charts`
- `GET /reports/timelines`

Reports use persisted paper-mode data only. If history is missing, the API returns `unknown`, `insufficient_data`, or `NOT_ENOUGH_HISTORY` instead of inventing outcomes.

`/reports/dashboard-charts` returns APK-friendly chart data for decision action
counts, confidence buckets, and paper-session scan status.

`/reports/timelines` returns APK-friendly chronological rows for AI decisions,
paper trade journal events, and audit events. It is paper/audit data only and
includes `live_trading_enabled=false` plus `public_data_only=true`.

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
