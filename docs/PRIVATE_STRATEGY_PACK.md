# Private Strategy Pack Boundary

Public code exposes safe strategy interfaces and placeholders. Production
strategy scoring formulas should be kept private and loaded later from private
server-side modules or protected backend configuration.

Rules:

- Do not hardcode proprietary whale scoring formulas in the public APK.
- Do not put production scoring weights in public client code.
- Public strategies must remain evidence-first and paper-safe.
- Missing data must return no signal, `SKIP`, or insufficient-data status.
- No strategy may promise profit or assume market movement.

The boundary helper lives at:

`trading_os/strategies/private_strategy_boundary.py`
