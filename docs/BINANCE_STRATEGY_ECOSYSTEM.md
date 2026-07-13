# Binance Strategy Ecosystem

The Binance strategy ecosystem is a paper/advisory-only map of strategy modules
for the TTRL AI Trading OS.

It does not enable live trading, withdrawals, margin, futures, transfers, or
direct APK order execution.

## Families

- Candle / Structure
- Order Book / Liquidity
- Whale / Volume
- News / Exchange Risk
- Risk / Local AI / Master Combiner

## API

- `GET /settings/strategy-catalog`

The catalog returns strategy names, required data, safety rules, and master
rules. Every strategy must obey:

- No Data = No Trade
- No Proof = No Decision
- Conflicts = HOLD/SKIP
- Risk unsafe = SKIP
- Low confidence = SKIP
- External AI key required: no
- Live execution available: false
