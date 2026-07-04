# Phase 4 Advanced Market Intelligence Layer

Phase 4 adds evidence-first market intelligence modules to the AI Binance Trading OS backend.

This phase does not build an APK, does not build an EXE, does not enable live trading, and does not place real Binance orders.

```text
Default mode: paper/sandbox
Live trading: disabled
Withdraw logic: forbidden
Margin/futures execution: not supported
Architecture: Binance Spot only
```

## Market Intelligence Flow

```text
MarketData
-> Market Intelligence
-> Multi-Factor Signal Combiner
-> AI Decision Brain
-> Zero Hallucination
-> Risk Engine
-> Execution Intent
-> Paper Simulator
```

Every output is evidence-backed. If required data is missing, the combined signal returns `SKIP`. If major signals conflict, the combined signal returns `SKIP` or `HOLD`.

## Candle Intelligence Engine

Module:

```text
trading_os/intelligence/candle_intelligence.py
```

The candle engine analyzes multi-timeframe candles for:

- trend direction
- breakout behavior
- reversal behavior
- wick rejection
- engulfing candles
- volume confirmation
- candle confidence score

Supported timeframes remain:

- `1m`
- `5m`
- `15m`
- `1h`
- `4h`

If candle data is absent, the engine returns missing data and no directional claim.

## Order Book Intelligence

Module:

```text
trading_os/intelligence/order_book_intelligence.py
```

The order book engine analyzes:

- buy walls
- sell walls
- bid/ask imbalance
- liquidity gaps
- spread risk
- fake wall suspicion markers
- order book confidence score

It does not claim liquidity support unless a snapshot is available.

## Whale Intelligence v1

Module:

```text
trading_os/intelligence/whale_intelligence_v1.py
```

Whale intelligence v1 supports:

- large trade detection
- large volume spike detection
- exchange activity placeholder
- whale confirmation score
- fake movement filter

If whale trade data is missing, the module returns `missing_data` and no whale signal. It does not invent whale movement.

## News Risk Intelligence

Module:

```text
trading_os/intelligence/news_risk_intelligence.py
```

News risk intelligence includes adapter skeletons for:

- Binance announcements
- crypto news feeds

It flags:

- listing/delisting risk
- regulatory risk
- negative sentiment emergency risk

Every news item must include a source and timestamp. Missing sources or timestamps are treated as invalid evidence.

## Market Structure Engine

Module:

```text
trading_os/intelligence/market_structure.py
```

The market structure engine analyzes:

- support and resistance
- liquidity zones
- trend structure
- higher-high and lower-low behavior
- range versus trend classification
- volatility regime

The engine only emits claims supported by candle evidence.

## Multi-Factor Signal Combiner

Module:

```text
trading_os/intelligence/signal_combiner.py
```

The combiner merges:

- candle signal
- order book signal
- whale signal
- news risk signal
- market structure signal

Output fields:

- `bullish_score`
- `bearish_score`
- `risk_score`
- `confidence_score`
- `conflicts`
- `missing_data`
- `final_signal`

Allowed final signals:

- `BUY`
- `SELL`
- `HOLD`
- `SKIP`

Rules:

- required data missing returns `SKIP`
- high news or market risk returns `SKIP`
- strong signal conflict returns `SKIP`
- low confidence returns `SKIP`
- all scores must come from evidence-backed module output

## Pipeline Integration

Module:

```text
trading_os/pipeline/decision_to_trade.py
```

The decision-to-trade pipeline now runs market intelligence before strategy placeholders and the AI decision brain.

The combined signal is converted into a normal signal assessment and then passed through:

- AI decision rules
- zero-hallucination verification
- risk checks
- execution intent creation
- paper simulation

Live order placement remains blocked.

## Audit Events

The audit logger records:

- candle analysis
- order book analysis
- whale analysis
- news risk analysis
- market structure analysis
- combined signal result
- missing data
- conflict reasons

These events are JSONL records suitable for future dashboard or database integration.

## Safety Invariants

- Live trading remains disabled.
- No real credentials are stored.
- No hardcoded secrets are added.
- No withdraw logic exists.
- No margin or futures execution exists.
- Binance Spot remains the only exchange architecture boundary.
- Decisions must be evidence-first.
- No unsupported whale, news, candle, or order-book claims are allowed.
