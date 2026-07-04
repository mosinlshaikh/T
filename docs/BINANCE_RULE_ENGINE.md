# Binance Rule Engine

Module:

```text
trading_os/binance/
trading_os/connectors/binance_spot.py
```

`backend/app/binance/` is experimental and is not the final integration target.

The Binance rule engine is Spot-only and validates:

- minimum order size
- tick size
- lot size
- step size
- price precision
- quantity precision
- minimum notional
- active trading pair status
- insufficient balance
- rate-limit-aware design
- exchange maintenance state

Real order execution is not implemented. `BinanceSpotClient.execute_order()` raises by design.

Withdrawals and private key support are forbidden.
