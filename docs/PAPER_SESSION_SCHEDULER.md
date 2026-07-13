# Paper Session Scheduler

The paper session scheduler runs repeated public-market paper scans for the
TTRL AI Trading OS.

It is designed to build paper decision history for:

- local AI learning
- strategy performance review
- decision audit
- dashboard monitoring
- future phone drill-down screens

## API

- `POST /control/paper-session/start`
- `POST /control/paper-session/stop`
- `GET /control/paper-session/status`

## Safety

- paper mode only
- public market data only
- no Binance private endpoints
- no live order execution
- no withdrawals
- no margin/futures
- emergency stop blocks new sessions

The scheduler is a data-collection and paper decision engine. It is not a
real-money trading engine.
