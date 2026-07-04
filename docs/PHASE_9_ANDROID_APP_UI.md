# Phase 9 Android APK Source and UI/UX Scaffold

Phase 9 creates Android source code only. It does not build an APK and does not generate an APK file.

```text
APK role: control panel, dashboard, alerts, settings, reports
Backend role: AI brain, Binance API, risk engine, order intent, paper simulator, runtime supervisor
Default mode: paper
Live trading: BLOCKED / DISABLED
Withdrawals: unsupported
Direct Binance execution from APK: forbidden
```

## Android Source Location

```text
android_app/
```

The scaffold uses Kotlin and Jetpack Compose-style source:

- `MainActivity`
- Compose theme
- navigation route model
- reusable UI components
- ViewModel
- repository layer
- backend API client skeleton
- data models matching the backend API contract
- 10 source screens for the APK dashboard/control experience

No Binance API key or secret belongs in this source tree.

## Screens

Implemented screens:

1. Splash / Boot
2. Dashboard
3. Market Intelligence
4. Trade Control
5. Portfolio
6. Decisions
7. Trade Journal
8. Reports
9. Settings
10. Audit / Safety

Each relevant screen displays paper/research mode, live trading disabled, withdrawals unsupported, no guaranteed profit, and evidence-first decision language.

## API Client Skeleton

Module:

```text
android_app/app/src/main/java/com/ttechnologyresearchlab/tradingos/network/BackendApiClient.kt
```

The APK talks only to backend API endpoints. It does not call Binance directly.

Client methods are scaffolded for:

- status
- health
- Binance readiness
- shutdown
- portfolio
- trades
- decisions
- audit
- reports
- controls
- settings

The backend base URL is a settings value. Android emulator default is `http://10.0.2.2:8000`.

## UI/UX Direction

The app uses a premium dark/gold trading dashboard direction:

- dark background
- gold accents
- glass-style cards
- prominent emergency stop
- safety labels
- mobile-first scan layout
- professional dashboard controls

The APK is dashboard/control-first, not exchange-execution-first.

## Development Preview Data

Fallback data is clearly labeled:

```text
DEVELOPMENT PREVIEW DATA
```

Preview data is only for UI development when the backend is unavailable. It must not be presented as real trading data.

## Emergency Stop UX

Emergency stop is visually prominent.

Graceful shutdown explains:

- new trades are blocked immediately
- active paper trades are managed safely
- logs are saved
- bot stops after safe state

## Security Invariants

- No Binance API key inside APK source.
- No Binance secret key inside APK source.
- No real credentials.
- No withdrawal support.
- No live trading enable button.
- No direct Binance order execution from APK.
- App talks only to backend API.
- Paper mode is default.
- Live trading status displays as blocked/disabled.

APK build should happen only after an explicit final build command.

## Phase 9B Polish Addendum

Phase 9B adds English/Hinglish language support, API Setup Wizard, Bot Brain explanation, Safety Lock, App Lock, onboarding, offline backend handling, strategy/notification settings polish, and release readiness checklist.

See:

[docs/PHASE_9B_PRE_APK_POLISH.md](PHASE_9B_PRE_APK_POLISH.md)
