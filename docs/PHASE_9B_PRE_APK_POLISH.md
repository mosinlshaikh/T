# Phase 9B Pre-APK UI/UX Polish

Phase 9B upgrades the Android source scaffold before final testing and APK build.

Android product direction and TTRL AI Trading OS authorship are attributed to
**MOSIN LIYAKAT SHAIKH**, Founder / Architect of T TECHNOLOGY RESEARCH LAB.

This app branding is not limited to Binance. The Android app represents the
broader TTRL AI Trading OS / T Financial Intelligence OS command center.

No APK, AAB, or EXE is built in this phase.

```text
APK role: control panel, dashboard, alerts, reports, settings, safety UI
Backend role: AI brain, Binance API, risk engine, paper simulator, runtime supervisor
Default mode: paper
Live trading: BLOCKED / DISABLED
Withdrawals: unsupported
Direct Binance execution from APK: forbidden
```

## License Activation UI

The Android source includes a License Activation screen for TTRL app activation
keys.

Important distinction:

- TTRL license key: app/backend access control.
- Binance API key: created separately inside Binance and handled only through
  backend/vault setup.

The APK source does not generate license keys, does not store Binance secrets,
does not support withdrawals, and does not execute Binance orders directly.

The license screen supports English/Hinglish labels and displays backend-offline
status safely when `/license/validate` is unavailable.

Phase 10 review confirms the app validates TTRL licenses only. It does not
generate TTRL keys, submit Binance keys, enable live trading, or execute Binance
orders.

## Language Support

The Android source now includes a lightweight language helper:

```text
android_app/app/src/main/java/com/ttechnologyresearchlab/tradingos/localization/AppLanguage.kt
```

Supported app languages:

- English
- Hinglish

Examples:

- Paper Mode Active -> Paper Mode Active hai
- Live Trading Disabled -> Live Trading Disabled hai
- No Data = No Trade -> Data nahi hai = Trade nahi
- Conflict = Skip/Hold -> Conflict hai = Skip ya Hold
- Withdrawals Unsupported -> Withdrawals supported nahi hai
- Evidence First Decision -> Evidence ke basis par decision

The Settings screen includes a language selector.

## New Screens

Added navigation entries and screen scaffolds:

- API Setup Wizard
- Bot Brain
- Safety Lock
- Release Readiness
- App Lock / Unlock
- Onboarding

The existing 10 Phase 9 screens remain present.

## API Setup Wizard

The setup wizard guides the user through:

- backend URL configured
- backend connection status
- API vault status
- Binance readiness status
- reading permission expected
- spot trading permission expected/future
- withdraw permission OFF required
- paper mode active
- live trading blocked
- safety score available

No API key entry screen is added.

## Bot Brain

The Bot Brain screen explains:

- latest AI decision
- confidence
- candle signal
- whale signal
- order book signal
- news risk
- market structure
- missing data
- conflicts
- zero-hallucination result
- risk result
- plain-language decision explanation

If data is missing, the UI shows missing/unknown. It does not invent market facts.

## Safety Lock

The Safety Lock screen shows:

- live trading disabled
- withdrawals unsupported
- paper mode active
- 10% reserve lock
- 5% max risk rule
- stop-loss required
- take-profit required
- emergency stop enabled
- zero hallucination active
- No Data = No Trade
- Conflict = Skip/Hold

Safety labels support `SAFE`, `CAUTION`, `DANGER`, and `UNKNOWN`.

## Offline Handling

The Android source includes:

- `BackendStatusBanner`
- backend states: `CONNECTED`, `DISCONNECTED`, `DEGRADED`, `UNKNOWN`
- reconnect action
- last known bot state placeholder
- last heartbeat placeholder
- safe fallback preview data
- disabled backend control buttons while disconnected

Preview data is explicitly labeled:

```text
DEVELOPMENT PREVIEW DATA
```

## App Lock

The app lock scaffold includes:

- 4-digit PIN placeholder
- unlock screen
- lock action from Settings
- biometric placeholder text

The lock protects dashboard/control access only. No Binance secrets exist in APK source or local app-lock storage.

## Strategy and Notification Settings

The Settings screen now includes:

- strategy control placeholders
- notification alert placeholders
- Telegram / WhatsApp / Email adapter placeholders

These settings are UI/backend-controlled placeholders only and have no live trading impact.

## Release Readiness

The Release Readiness screen shows:

- backend connected
- database ready
- paper mode active
- live trading blocked
- withdrawals unsupported
- safety score
- last heartbeat
- API readiness
- audit logging active
- no secrets in app
- final APK build pending

## Safety Invariants

- No Binance API key in APK source.
- No Binance secret key in APK source.
- No real credentials.
- No withdrawal support.
- No live trading enable button.
- No direct Binance order placement from app.
- Live trading displays as blocked/disabled.
- Paper mode remains default.
- APK build happens only after explicit final build command.
