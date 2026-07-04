# Phase 3 Trade Lifecycle, Portfolio State, and Execution Intent Layer

Phase 3 adds the backend trade lifecycle and paper execution foundation for the AI Binance Trading OS.

This phase still does not build an APK or EXE, does not enable live trading, and does not place real Binance orders.

```text
Default mode: paper/sandbox
Live trading: disabled
Withdraw logic: forbidden
Margin/futures execution: not supported
Architecture: Binance Spot only
```

## Trade Lifecycle Engine

Module:

```text
trading_os/trade/lifecycle.py
```

Trade states:

- `NEW_SIGNAL`
- `RISK_CHECK_PENDING`
- `APPROVED_FOR_PAPER`
- `PAPER_OPEN`
- `PAPER_PARTIAL_EXIT`
- `PAPER_CLOSED`
- `LIVE_BLOCKED`
- `REJECTED_BY_RISK`
- `REJECTED_BY_ZERO_HALLUCINATION`
- `CANCELLED`

The lifecycle validator rejects invalid state transitions. If any live path is attempted, the state can be forced to `LIVE_BLOCKED`.

`TradeContext` carries:

- symbol
- timeframe
- side
- entry
- stop loss
- take profit
- confidence
- evidence
- risk info
- timestamps

## Execution Intent Layer

Module:

```text
trading_os/execution/intent.py
```

The execution layer creates order intents only. It never places real exchange orders.

Supported intent types:

- `MARKET_BUY`
- `MARKET_SELL`
- `LIMIT_BUY`
- `LIMIT_SELL`
- `STOP_LOSS`
- `TAKE_PROFIT`
- `PARTIAL_EXIT`

Every intent includes:

- symbol
- side
- quantity
- optional price
- stop loss
- take profit
- reason
- evidence IDs
- risk approval ID
- `live_enabled=false`

## Paper Trading Simulator v1

Module:

```text
trading_os/paper/simulator.py
```

The simulator supports:

- open paper trade
- close paper trade
- partial exit
- stop-loss hit
- take-profit hit
- simple fee model
- journal records for simulated trades

It refuses any intent where `live_enabled=true`.

## Portfolio State Manager

Module:

```text
trading_os/portfolio/state.py
```

The portfolio manager tracks:

- USDT wallet snapshot
- open positions
- closed positions
- exposure
- available capital
- reserve capital lock
- daily PnL
- drawdown
- realized and unrealized PnL

## Strategy Registry

Module:

```text
trading_os/strategies/registry.py
```

Initial strategy placeholders:

- `WHALE_CONFIRMATION_STRATEGY`
- `CANDLE_STRUCTURE_STRATEGY`
- `NEWS_RISK_FILTER_STRATEGY`
- `ORDER_BOOK_LIQUIDITY_STRATEGY`
- `MULTI_FACTOR_AI_STRATEGY`

Strategies must return evidence-based signals only. If required evidence is missing, the strategy returns no signal. Low-confidence evidence returns a `SKIP` signal.

No strategy is allowed to invent whale, news, candle, or order-book claims.

## Decision-to-Trade Pipeline

Module:

```text
trading_os/pipeline/decision_to_trade.py
```

Flow:

```text
MarketData
-> Strategy Signals
-> AI Decision Brain
-> Zero Hallucination Verification
-> Risk Engine
-> Execution Intent
-> Paper Simulator
-> Trade Journal
```

Pipeline behavior:

- shutdown requested blocks new trade intents
- zero-hallucination rejection stops the trade
- HOLD/SKIP decisions do not produce intents
- risk rejection stops the trade
- approved decisions create paper intents only
- paper fills update portfolio state and journal

## Smart Shutdown Integration

When shutdown is requested:

- new trade intents are blocked immediately
- active paper trades remain managed
- stop-loss/take-profit/exit intents are allowed
- lifecycle state can be saved through audit/journal layers
- the system moves to `SAFELY_STOPPED` only after no unsafe active state remains

Emergency stop moves to `EMERGENCY_STOPPED`.

## Audit and Journal Events

The audit logger now supports:

- trade lifecycle transition
- execution intent creation
- paper order fill
- partial exit
- stop-loss event
- take-profit event
- portfolio snapshot
- strategy signal
- decision-to-trade pipeline result

## Safety Invariants

- Live trading remains impossible by default.
- `LIVE_BLOCKED` behavior is explicit.
- No withdrawal logic exists.
- No margin/futures execution exists.
- Spot-only architecture.
- No profit guarantee language.
- No hallucinated whale/news/candle/order-book claims.
