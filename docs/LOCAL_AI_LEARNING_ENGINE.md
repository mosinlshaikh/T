# Local AI Learning Engine

This project uses a local, evidence-only learning layer. It does not require
OpenAI, Gemini, or any external AI API key.

## Purpose

The local AI engine reviews persisted paper-mode evidence:

- AI decisions
- strategy signals
- paper trade journal entries
- risk rejections
- zero-hallucination blocks
- market intelligence snapshots

It produces advisory scoring only. It does not automatically change production
strategy rules, does not enable live trading, and does not place Binance orders.

## Guardrails

- No Data = No Trade
- No Proof = No Decision
- paper-only learning mode
- auto strategy changes disabled
- live trading impact disabled
- no guaranteed profit language
- no fake whale or news claims
- risk and zero-hallucination gates stay active

## API

- `GET /learning/local-ai`
- `GET /learning/market-king-score`
- `GET /learning/recommendations`

The phrase "market king score" means local evidence readiness. It is not a
profit guarantee and must not be treated as a prediction.
