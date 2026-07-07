# Release Draft: v0.1.0-paper-alpha

Release title:

```text
TTRL AI Trading OS v0.1.0 Paper Alpha
```

## Highlights

- Evidence-first backend foundation
- Android dashboard/control app source
- Live public-market paper monitor
- Paper auto trader loop
- AI decision brain with `BUY` / `SELL` / `HOLD` / `SKIP`
- Zero-hallucination verification
- Risk engine and capital rules
- Paper simulator, trade journal, and audit logger
- SQLite persistence and memory layer
- TTRL app license key system
- Go monitor probe scaffold
- Rust safety guard scaffold
- Public/private strategy boundary documentation

## Safety Position

This release is paper-mode only.

```text
LIVE_TRADING_ENABLED=false
MANUAL_LIVE_UNLOCK=false
BINANCE_WITHDRAWALS_SUPPORTED=false
```

No real Binance orders are placed. No withdrawals are supported. No profit is
guaranteed.

## Demo Routes

- `GET /status/health`
- `GET /monitor/paper-live`
- `POST /control/paper-auto-trader/tick`
- `GET /control/paper-auto-trader/status`

## Known Limits

- News and whale sources are still early-stage.
- Android chart drill-down modal is pending.
- 30-day paper logbook automation is pending.
- Rust source is present, but local Rust toolchain may be required to compile.
- Live trading is intentionally blocked.

## Suggested Release Assets

- Source archive
- README screenshots
- Android source
- No keystore
- No secrets
- No production APK unless separately approved

