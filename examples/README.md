# T Examples

This folder contains practical examples for using T as a research-only financial intelligence system.

```text
Research only. Not financial advice.
```

## Available Examples

| Example | Command | Purpose |
| --- | --- | --- |
| Safety guard demo | `python -m examples.safety_guard_demo` | Test hallucination-resistant output guard |
| Backtest demo | `python -m examples.backtest_demo` | Run a sample backtest and review analytics |
| Dashboard demo | `python -m streamlit run dashboard/app.py` | Launch the T Mission Dashboard |

## Safety Guard Demo

Run:

```bash
python -m examples.safety_guard_demo
```

This example shows how T detects unsafe research-output language, sanitizes blocked claims, and appends the research-only disclaimer.

## Backtest Demo

Run:

```bash
python -m examples.backtest_demo
```

This prints the backtest analytics summary, equity curve, and generated trade list.

## Dashboard Demo

Run:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard shows mission control, backtest analytics, raw report inspection, and project status.

## Recommended Research Workflow

1. Load sample/demo data.
2. Run scoring or backtest.
3. Review output metrics.
4. Review equity curve and trade table.
5. Check safety status.
6. Apply human review.
7. Do not treat output as financial advice.

## Disclaimer

T is research-only software. It does not provide financial advice, investment advice, trade recommendations, portfolio management, or profit assurance.

```text
T
T Technology Research Lab
```
