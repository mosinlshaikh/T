# Demo Walkthrough

This walkthrough shows how a reviewer can understand the system without real
Binance credentials or live trading.

## 1. Check Backend Health

```bash
curl https://t-production-8efc.up.railway.app/status/health
```

Expected safety properties:

- `mode` is `paper`
- `live_trading_enabled` is `false`
- withdrawals are unsupported
- API readiness is safe for paper mode

## 2. Run One Paper Market Tick

```bash
curl -X POST https://t-production-8efc.up.railway.app/control/paper-auto-trader/tick
```

Expected result:

- action is one of `BUY`, `SELL`, `HOLD`, `SKIP`
- confidence is included
- reason is included
- no real order is placed
- paper fill is created only if risk and verification allow it

## 3. Inspect Live Paper Monitor

```bash
curl https://t-production-8efc.up.railway.app/monitor/paper-live
```

The monitor returns:

- latest decision
- market snapshot
- candle analysis
- order book analysis
- whale analysis
- news risk analysis
- market structure analysis
- paper journal
- audit timeline
- portfolio state

## 4. Review Android Dashboard

The Android app is a control panel, not an exchange execution client.

Important screens:

- Dashboard
- Trade Control
- Bot Brain
- Decisions
- Trade Journal
- Audit / Safety
- Release Readiness
- License Activation

Every relevant screen should show paper mode and live trading disabled.

## 5. Paper Trade Interpretation

When a trade is not opened, that can be correct behavior. Examples:

- missing data -> `SKIP`
- conflicting signals -> `HOLD` or `SKIP`
- low confidence -> `SKIP`
- risk unsafe -> `SKIP`

The goal is not to force trades. The goal is to preserve evidence, explain the
decision, and avoid unsupported claims.

## 6. What Not To Expect

This public phase does not provide:

- guaranteed profit
- financial advice
- live Binance trading
- withdrawal support
- margin/futures execution
- hidden strategy formulas

