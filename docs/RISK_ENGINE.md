# Risk Engine

Module:

```text
trading_os/risk/
trading_os/security/kill_switch.py
```

`backend/app/risk/` is experimental and is not the final integration target.

Risk requirements:

- reserve capital: 10% untouched
- max active risk: 5%
- growth capital: 85%
- no all-in trade
- daily loss limit required
- consecutive loss cooldown required
- max open trades required
- stop-loss required
- take-profit required
- emergency kill switch required

If risk is unsafe, AI decision must return `SKIP`.
