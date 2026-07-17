# AI Trading OS Backend Foundation

T now includes a backend foundation package at `trading_os/`.

Project architect: **MOSIN LIYAKAT SHAIKH**, Founder / Architect of
**T TECHNOLOGY RESEARCH LAB**.

Product identity: **TTRL AI Trading OS / T Financial Intelligence OS**.
Binance Spot is one connector scope inside the backend, not the only product
direction.

`trading_os/` is the canonical backend. The `backend/` folder is retained as an
experimental scaffold only.

Current canonical architecture references:

- [Canonical Architecture](architecture/CANONICAL_ARCHITECTURE.md)
- [Module Ownership Map](architecture/MODULE_OWNERSHIP_MAP.md)
- [Legacy and Deprecated Modules](architecture/LEGACY_AND_DEPRECATED_MODULES.md)
- [Phase 0 Baseline Architecture Audit](audits/BASELINE_ARCHITECTURE_AUDIT.md)

CI includes an import-boundary check via `scripts/check_import_boundaries.py` so
canonical `trading_os/` code cannot accidentally depend on legacy roots such as
`backend/`, root `api/`, `core/`, `modules/`, `nexus/`, `enterprise/`, or
`realworld/`.

This is not a live trading system. It is a safe backend architecture skeleton
created under the direction of **MOSIN LIYAKAT SHAIKH** for market data,
AI-assisted research decisions, paper trading workflows, risk controls, audit
trails, and future mobile/API integration.

```text
Research only. Not financial advice.
Live trading execution is disabled by default.
Withdraw permissions are not supported.
```

## TTRL App Licensing

The backend includes a server-side TTRL app license system under
`trading_os/licensing/`.

This is not a Binance API key generator. It creates TTRL app activation keys for
client access control. Binance API keys must still be created inside Binance and
handled through the backend vault flow.

Safety remains unchanged:

- Live trading disabled by default.
- Paper mode default.
- Withdrawals unsupported.
- No real Binance execution in the Android app.
- No license key or admin token hardcoded in repo.

## Phase 10 Release Readiness

Final pre-APK review uses `trading_os/` as the backend source of truth. Checks
cover syntax/imports, pytest, API routes, SQLite persistence, paper pipeline
smoke, smart shutdown, reports, safety score, settings persistence, TTRL license
validation, Android source review, API contract verification, and static safety
scans.

The final APK build is the next phase and must be triggered separately. No APK,
AAB, EXE, live trading, live Binance call, withdrawal, margin, or futures support
is enabled by this backend.

## Non-Negotiable Safety Rules

- No real API keys in source code.
- No secrets committed to the repository.
- No withdraw permission support.
- Live trading remains disabled by default.
- Paper/sandbox mode is the default runtime mode.
- Every AI decision must require data evidence.
- If required data is missing, the decision must be `SKIP`.
- If signals conflict, the decision must be `SKIP` or `HOLD`.
- Every future execution-capable pathway must pass the emergency kill switch, risk engine, capital manager, and audit logger.

## Package Layout

```text
trading_os/
|-- config.py
|-- orchestrator.py
|-- connectors/
|   |-- binance_spot.py
|   |-- rest_api.py
|   `-- websocket_market_data.py
|-- market/
|   |-- market_data_engine.py
|   |-- candle_engine.py
|   `-- order_book_engine.py
|-- ai/
|   |-- decision_types.py
|   |-- decision_brain.py
|   `-- verified_decision_engine.py
|-- intelligence/
|   |-- whale_intelligence.py
|   `-- news_intelligence.py
|-- risk/
|   |-- risk_engine.py
|   `-- capital_manager.py
|-- audit/
|   |-- audit_logger.py
|   `-- trade_journal.py
|-- database/
|   `-- models.py
`-- security/
    |-- api_key_vault.py
    `-- kill_switch.py
```

## Component Responsibilities

| Component | Responsibility | Current Status |
| --- | --- | --- |
| `TradingOSConfig` | Safe runtime defaults | Paper mode, live disabled |
| `BinanceSpotConnector` | Binance Spot request/subscription skeleton | Public data only |
| `RestApiConnector` | REST request builder skeleton | Private requests disabled |
| `WebSocketMarketDataConnector` | Public stream URL/subscription skeleton | Public market data only |
| `MarketDataEngine` | Tick ingestion and latest tick lookup | Skeleton |
| `CandleEngine` | Candle construction path | Skeleton |
| `OrderBookEngine` | Order book snapshot and spread calculation | Skeleton |
| `AIDecisionBrain` | Deterministic proposal builder | No LLM call yet |
| `VerifiedDecisionEngine` | Evidence gate for zero-hallucination decisions | Enforces `SKIP`/`HOLD` rules |
| `WhaleIntelligenceEngine` | Whale evidence skeleton | No external provider yet |
| `NewsIntelligenceEngine` | News evidence skeleton | No external provider yet |
| `RiskEngine` | Risk policy checks | Skeleton |
| `CapitalManager` | Paper allocation checks | Skeleton |
| `AuditLogger` | JSONL audit event writer | Skeleton |
| `TradeJournal` | Paper decision/trade notes | In-memory skeleton |
| `database.models` | Persistence model skeletons | Dataclasses only |
| `ApiKeyVaultDesign` | Secret-handling design boundary | No raw key storage |
| `EmergencyKillSwitch` | Halt/clear/assert safety control | Skeleton |
| `TradeLifecycleEngine` | Trade state transition validation | Phase 3 |
| `ExecutionIntentLayer` | Converts approved decisions into paper order intents | Phase 3 |
| `PaperTradingSimulator` | Paper-only trade fills, exits, SL/TP events | Phase 3 |
| `PortfolioStateManager` | Wallet, exposure, reserve, PnL, drawdown state | Phase 3 |
| `StrategyRegistry` | Evidence-only strategy placeholders | Phase 3 |
| `DecisionToTradePipeline` | Market-data-to-paper-trade pipeline with stage audit results | Phase 3+ |
| `CandleIntelligenceEngine` | Candle trend, breakout, reversal, wick, volume analysis | Phase 4 |
| `OrderBookIntelligenceEngine` | Wall, imbalance, liquidity gap, spread risk analysis | Phase 4 |
| `WhaleIntelligenceV1` | Large trade and volume spike evidence analysis | Phase 4 |
| `NewsRiskIntelligenceEngine` | Source/timestamp-backed announcement and risk flags | Phase 4 |
| `MarketStructureEngine` | Support/resistance, structure, volatility regime analysis | Phase 4 |
| `MultiFactorSignalCombiner` | Evidence-backed combined signal scoring | Phase 4 |
| `ApiKeyVaultDesign` | Secret provider design and availability checks only | Phase 5 |
| `BinanceApiPermissionVerifier` | Safe API readiness and permission metadata checks | Phase 5 |
| `RuntimeSupervisor` | 24x7 heartbeat, crash guard, reconnect, safe shutdown skeleton | Phase 5 |
| `NotificationEngine` | Telegram, WhatsApp, and email adapter placeholders | Phase 5 |
| `health_models` | Response models for future APK/API health views | Phase 5 |
| `trading_os.api.app` | FastAPI-compatible backend API app skeleton | Phase 6 |
| `trading_os.api.routes.*` | Status, control, portfolio, trades, decisions, audit, settings routes | Phase 6 |
| `TradingOSRepository` | SQLite-backed CRUD-style persistence layer | Phase 7 |
| `BotMemory` | Evidence-based persisted memory summaries | Phase 7 |
| `DailyPerformanceSummary` | Durable daily paper performance summaries | Phase 7 |
| `StrategyPerformanceAnalyzer` | Persisted paper strategy analytics | Phase 8 |
| `DecisionReviewEngine` | Evidence-based decision review labels | Phase 8 |
| `LearningFeedbackEngine` | Advisory-only learning feedback | Phase 8 |
| `ReportGenerator` | Daily/performance/risk/safety report generation | Phase 8 |
| `SafetyScoreEngine` | 0-100 safety score and recommended action | Phase 8 |
| `android_app/` | Kotlin/Jetpack Compose Android source scaffold | Phase 9 |
| Android polish | Setup wizard, bilingual UI, app lock, offline handling, release checklist | Phase 9B |
| Final review | Integration validation, security review, and release readiness | Phase 10 |

## Decision Safety Flow

```text
Public market data
  -> market data / candle / order book engines
  -> candle / order book / whale / news / structure intelligence
  -> multi-factor signal combiner
  -> risk/capital evidence
  -> AI decision brain proposal
  -> verified decision engine
  -> SKIP / HOLD / BUY / SELL intent
  -> audit logger and trade journal
```

The verified decision engine requires evidence from:

- `market_tick`
- `risk_check`
- `capital_check`

If one of these is missing, the decision is `SKIP`.

If evidence exists but signals disagree, the decision is `HOLD`.

## API Key Vault Design

The repository only includes `ApiKeyVaultDesign`, which validates metadata and rejects withdraw permissions. It does not store raw API keys.

Future implementations should store secrets outside git using one of:

- OS keychain
- Cloud KMS
- Encrypted local vault outside the repository
- Mobile secure enclave or keystore for APK clients

Any future key must be read-only or trading-limited. Withdraw permission remains forbidden.

## Live Trading Boundary

`BinanceSpotConnector.execute_order()` raises an error by design.

Before any future live trading phase, the project must add:

- separate audited branch
- explicit user opt-in
- sandbox-first exchange testing
- risk engine hard limits
- capital manager hard limits
- emergency kill switch enforcement
- audit trail verification
- test coverage for failure modes
- documentation update

Until then, the backend supports research, paper mode, and architecture preparation only.

## Phase 3 Trade Lifecycle

Phase 3 is documented in:

[docs/PHASE_3_TRADE_LIFECYCLE.md](PHASE_3_TRADE_LIFECYCLE.md)

It adds trade lifecycle state, execution intents, paper simulation, portfolio state, strategy placeholders, and a decision-to-trade pipeline. It does not enable live trading.

## Phase 4 Market Intelligence

Phase 4 is documented in:

[docs/PHASE_4_MARKET_INTELLIGENCE.md](PHASE_4_MARKET_INTELLIGENCE.md)

It adds evidence-backed candle intelligence, order book intelligence, whale intelligence v1, news risk intelligence, market structure analysis, and a multi-factor signal combiner. If required intelligence data is missing, the combined result is `SKIP`. Live trading remains disabled.

## Phase 5 Security Runtime

Phase 5 is documented in:

[docs/PHASE_5_SECURITY_RUNTIME.md](PHASE_5_SECURITY_RUNTIME.md)

It adds secure configuration loading, API vault provider interfaces, Binance API permission readiness checks, runtime supervisor state, notification placeholders, health response models, and runtime audit events. It does not expose secrets and does not enable live trading.

## Phase 6 Backend API Layer

Phase 6 is documented in:

[docs/API_CONTRACT_FOR_APK.md](API_CONTRACT_FOR_APK.md)

It adds a FastAPI-compatible API skeleton for future Android APK integration. The API exposes status, control, portfolio, trades, decisions, audit, and settings routes. It does not add live trading, credential submission, withdrawal support, or real order placement.

## Phase 7 Database Memory

Phase 7 is documented in:

[docs/PHASE_7_DATABASE_MEMORY.md](PHASE_7_DATABASE_MEMORY.md)

It adds SQLite persistence, repository methods, evidence-based memory, durable bot state, persisted settings, audit persistence, and daily paper performance summaries. Secrets are redacted and never stored.

## Phase 8 Analytics Reports

Phase 8 is documented in:

[docs/PHASE_8_ANALYTICS_REPORTS.md](PHASE_8_ANALYTICS_REPORTS.md)

It adds persisted paper-data analytics, decision review, advisory-only learning feedback, report generation, APK report routes, dashboard data contracts, and safety scoring. It does not modify strategy rules automatically and does not enable live trading.

## Phase 9 Android App UI Source

Phase 9 is documented in:

[docs/PHASE_9_ANDROID_APP_UI.md](PHASE_9_ANDROID_APP_UI.md)

It adds Android source code for a future APK control panel and dashboard. The APK scaffold talks only to the backend API and does not contain Binance credentials, live trading controls, withdrawal support, or direct exchange execution.

## Phase 9B Pre-APK Polish

Phase 9B is documented in:

[docs/PHASE_9B_PRE_APK_POLISH.md](PHASE_9B_PRE_APK_POLISH.md)

It adds English/Hinglish labels, API setup wizard, bot brain explanation, safety lock, app lock scaffold, onboarding, offline handling, strategy/notification UI sections, and release readiness checklist. It does not build an APK and does not enable live trading.

## Phase 10 Final Review

Phase 10 is documented in:

[docs/PHASE_10_FINAL_REVIEW.md](PHASE_10_FINAL_REVIEW.md)

It validates backend imports, tests, API routes, persistence, paper flow, smart shutdown, security boundaries, Binance safety rules, Android source structure, and API contract consistency. It does not build an APK/AAB/EXE and does not enable live trading.

## Multi-Timeframe Candle Study

The backend includes an evidence-only candle study route:

- `GET /monitor/candle-study?symbol=BTCUSDT&timeframes=5m,10m,1h,4h,8h,24h,1M&limit=80`
- `5m`, `1h`, `4h`, `8h`, `24h`/`1d`, and `1M` use Binance public klines.
- `10m` is synthetic because Binance Spot does not provide a native 10-minute kline interval; the backend aggregates pairs of verified `5m` candles.
- Output explains why the latest candle moved up, down, or sideways using only observed candle evidence: price change, volume ratio, support/resistance range, wick pressure, breakout/breakdown, and candle body strength.
- Learning notes are advisory only. They do not auto-change strategy rules, enable live trading, or guarantee profit.

Safety rule remains unchanged: missing candle data returns missing-data output, and trading decisions must remain `SKIP` or `HOLD` when proof is insufficient or signals conflict.

## F&O / Derivatives Research Guard

The backend now includes paper-only derivatives research endpoints:

- `GET /derivatives/readiness`
- `GET /derivatives/risk-estimate?symbol=BTCUSDT&instrument=FUTURES&notional_usdt=100&leverage=2&adverse_move_pct=1`

These endpoints do not enable futures, options, leverage, margin, or live derivatives order placement. They only show readiness blockers and capped risk estimates so the Android app can explain why derivatives remain blocked in this build.

F&O is high risk. This project does not claim higher profit from derivatives. The current implementation is for education, paper review, and future architecture planning only.
