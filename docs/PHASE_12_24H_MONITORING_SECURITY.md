# Phase 12: 24h Paper Monitoring and Security Hardening

This phase stabilizes the Railway paper-monitoring loop and adds a
post-quantum-ready security posture for future production hardening.

## 24h Paper Monitoring

The backend exposes:

- `GET /monitor/24h-paper-status`
- `GET /control/paper-session/status`
- `GET /monitor/paper-scan-summary`
- `GET /reports/statement-daily`

The 24h status response includes:

- session running state
- uptime seconds and hours
- 24h target window
- scan count
- expected scan count
- 24h scan progress percent
- latest action, confidence, and blocker reason
- 24h statement PnL fields
- safety checks

The paper session can auto-resume on Railway with:

```env
T_PAPER_SESSION_ENABLED=true
T_PAPER_SESSION_SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT
T_PAPER_SESSION_TIMEFRAME=5m
T_PAPER_SESSION_INTERVAL_SECONDS=300
T_PAPER_SESSION_TRADE_NOTIONAL_USDT=50
```

This remains public-data paper monitoring only. It does not place real Binance
orders.

## Security Hardening

`GET /settings/security` now includes `post_quantum_security`.

This is a post-quantum-ready design posture, not a quantum-proof guarantee.
The current build uses standard platform TLS and does not implement custom
cryptography.

Active controls:

- no Binance secrets in APK
- no real secrets in repository
- no withdrawal support
- live trading disabled
- manual live unlock disabled
- TTRL license keys hashed at rest
- admin token must come from environment
- API errors are redacted
- evidence-first and zero-hallucination decision gates remain active

Future audited hardening can add hybrid TLS/PQC support when stable platform
libraries are available.

## Safety Statement

Paper mode remains default. Live trading, withdrawals, margin, futures, private
Binance execution, and any profit guarantee remain out of scope for this phase.

Redeploy marker: 2026-07-17T23:24:15Z
