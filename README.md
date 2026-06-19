# T

[![CI](https://github.com/mosin1982/T/actions/workflows/ci.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/ci.yml)
[![Docker Build](https://github.com/mosin1982/T/actions/workflows/docker.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/docker.yml)
[![Smoke](https://github.com/mosin1982/T/actions/workflows/smoke.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/smoke.yml)
[![Release](https://github.com/mosin1982/T/actions/workflows/release.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/release.yml)

**T** is an open-source **Financial Intelligence Operating System** by **T Technology Research Lab** for market research, paper trading, backtesting, risk analysis, smart money intelligence, and research-first financial automation workflows.

> **Research only. Not financial advice.**
> T is not a guaranteed-profit trading bot, investment advisor, live trading recommendation system, or real-money execution product.

---

## Important Links

| Resource                     | Link                                                                        |
| ---------------------------- | --------------------------------------------------------------------------- |
| GitHub Repository            | [github.com/mosin1982/T](https://github.com/mosin1982/T)                    |
| Latest Release               | [Releases / Latest](https://github.com/mosin1982/T/releases/latest)         |
| Current Recommended Release  | [v0.9.2-alpha](https://github.com/mosin1982/T/releases/tag/v0.9.2-alpha)    |
| First Stable Public Alpha    | [v0.8.2-alpha](https://github.com/mosin1982/T/releases/tag/v0.8.2-alpha)    |
| CI Workflow                  | [CI](https://github.com/mosin1982/T/actions/workflows/ci.yml)               |
| Docker Workflow              | [Docker Build](https://github.com/mosin1982/T/actions/workflows/docker.yml) |
| Smoke Workflow               | [Smoke](https://github.com/mosin1982/T/actions/workflows/smoke.yml)         |
| Release Workflow             | [Release](https://github.com/mosin1982/T/actions/workflows/release.yml)     |
| License                      | [LICENSE](LICENSE)                                                          |
| Disclaimer                   | [DISCLAIMER.md](DISCLAIMER.md)                                              |
| Security Policy              | [SECURITY.md](SECURITY.md)                                                  |
| Contributing Guide           | [CONTRIBUTING.md](CONTRIBUTING.md)                                          |
| Code of Conduct              | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)                                    |
| Support                      | [SUPPORT.md](SUPPORT.md)                                                    |
| Donate / Support Development | [DONATE.md](DONATE.md)                                                      |
| Changelog                    | [CHANGELOG.md](CHANGELOG.md)                                                |

---

## Overview

T is a public alpha research platform built to explore financial intelligence workflows safely and transparently.

It provides a foundation for:

* Market research
* Paper trading simulations
* Backtesting experiments
* Risk analysis
* Smart money intelligence workflows
* Event-driven financial research
* Lightweight data-lake experiments
* Mission-control health checks
* Dashboard-based research visibility

T is designed to be a **research-first platform**, not a profit-promise product.

---

## Current Release Status

Recommended release:

```text
v0.9.2-alpha
```

Release notes:

```text
v0.8.2-alpha  - First stable public alpha release
v0.9.2-alpha  - Dashboard alpha / latest clean release
```

Older intermediate releases such as `v0.9.0-alpha` and `v0.9.1-alpha` may exist as development attempts and should not be treated as the recommended version.

---

## Core Features

### Research Engine

* Demo mode for sample market-intelligence flow
* Research-only signal generation
* Alpha-score foundation
* Risk-label foundation
* Explainable signal output

### Backtesting Engine

* CSV-based backtesting
* Entry/exit simulation
* Fee and slippage support
* PnL calculation
* Win-rate calculation
* Profit-factor calculation
* Max-drawdown tracking
* JSON report output

### Paper Trading Foundation

* Virtual capital simulation
* Safe research-only execution model
* No real order placement
* Experimentation-first architecture

### Mission Control

* Repository health checks
* Sample-data checks
* Tests-folder checks
* Documentation checks
* Backtest-report checks
* Research-only status reporting

### Dashboard

* Streamlit-based Mission Dashboard
* Mission-control status viewer
* Backtest-report viewer
* Research-only warning panel
* Alpha roadmap visibility

### Platform Foundations

* Event sourcing foundation
* SQLite data lake foundation
* Plugin system foundation
* SDK skeleton
* API gateway skeleton
* Validation center
* Data-quality checks
* Benchmark strategy foundation

### DevOps and Release Automation

* GitHub Actions CI
* Docker Build workflow
* Smoke workflow
* Release workflow
* Public GitHub releases
* Security policy
* Contributing guide
* Code of Conduct
* Disclaimer and support files

---

## Installation

Clone the repository:

```bash
git clone https://github.com/mosin1982/T.git
cd T
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install development tools:

```bash
python -m pip install black ruff pytest
```

---

## Quick Start

Run demo mode:

```bash
python t_cli.py demo
```

Run backtest mode:

```bash
python t_cli.py backtest
```

Run mission control:

```bash
python t_cli.py mission-control
```

Run tests:

```bash
python -m pytest -q
```

Run code-quality checks:

```bash
python -m black --check .
python -m ruff check .
```

---

## Mission Dashboard

T includes a lightweight Streamlit Mission Dashboard for research visibility, mission-control checks, and backtest-report review.

Run locally:

```bash
python -m streamlit run dashboard/app.py
```

Then open:

```text
http://localhost:8501
```

Dashboard screenshot path:

```text
docs/images/t-mission-dashboard.png
```

If the screenshot exists in the repository, it will render here:

![T Mission Dashboard](docs/images/t-mission-dashboard.png)

---

## Backtest Report

After running:

```bash
python t_cli.py backtest
```

T saves a backtest report at:

```text
reports/backtests/backtest_report.json
```

Example report fields:

```json
{
  "starting_balance": 10000,
  "ending_balance": 10004.43,
  "max_drawdown_pct": 0,
  "win_rate_pct": 100,
  "profit_factor": "inf",
  "net_pnl": 4.43
}
```

This report is for research and testing only.

---

## Project Structure

```text
T/
├── agents/
├── alerts/
├── api/
├── backtest/
├── benchmark/
├── core/
├── dashboard/
├── datalake/
├── docs/
├── events/
├── mission_control/
├── modes/
├── modules/
├── nexus/
├── paper/
├── plugins/
├── quality/
├── realworld/
├── reports/
├── sdk/
├── tests/
├── validation/
├── t_cli.py
├── requirements.txt
├── README.md
├── LICENSE
├── DISCLAIMER.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── DONATE.md
└── SUPPORT.md
```

---

## CLI Commands

### Demo Mode

```bash
python t_cli.py demo
```

Runs the sample research/demo mode.

### Backtest Mode

```bash
python t_cli.py backtest
```

Runs the backtest engine and saves a JSON report.

### Mission Control

```bash
python t_cli.py mission-control
```

Shows system health and readiness checks.

### Real-World Observation Mode

If available in your local setup:

```bash
python t_cli.py real-binance --symbol btcusdt --threshold 3.0
```

This is observation-only and does not place trades.

---

## Safety Positioning

T is intentionally positioned as:

```text
Research software
Paper trading foundation
Backtesting framework
Financial intelligence workflow platform
```

T is **not**:

```text
Guaranteed-profit trading software
Financial advice
Investment advice
Live trading recommendation software
Real-money execution system
```

Always use T responsibly.

---

## Commercial Use and Professional Services

The source code may be publicly available through GitHub, but professional services can be charged separately.

Possible paid services include:

* Setup and installation
* Dashboard customization
* Strategy module development
* Backtest/report customization
* Data integration
* Training
* Deployment
* Business integration
* Monthly support

Suggested service positioning:

```text
Source access: public alpha / GitHub
Setup and support: paid
Customization and integration: paid
Enterprise/R&D work: custom quotation
```

Indicative INR pricing for services:

```text
Basic demo/setup: ₹5,000 – ₹15,000
Professional installation/training: ₹15,000 – ₹35,000
Custom dashboard/reporting: ₹25,000 – ₹75,000
Custom strategy module: ₹30,000 – ₹1,00,000
Business/custom integration: ₹75,000 – ₹2,50,000+
Monthly support: ₹5,000 – ₹50,000/month
Enterprise/R&D version: ₹2,50,000 – ₹10,00,000+
```

These are service fees, not trading-performance fees.

---

## Donate / Support Development

T is developed as a public alpha research project by **T Technology Research Lab**.

If this project helps your research, learning, testing, or development workflow, you can support the project through donations or paid professional services.

### Donation Options

| Method      | Details                              |
| ----------- | ------------------------------------ |
| UPI         | `tmps8346991530153183@slc`           |
| Binance UID | `475627577`                          |
| USDT TRC20  | `TLFLEDbN47bSBkWeqZzMNgkrzRK64RHbVn` |

### Important Donation Notice

Donations are voluntary and do not create any investment relationship, trading promise, profit guarantee, financial advisory relationship, or service obligation.

T remains:

```text
Research only. Not financial advice.
```

For setup, training, dashboard customization, business integration, or enterprise R&D work, use paid professional service engagement instead of donation.

---

## Development Workflow

Recommended workflow:

```bash
git checkout -b feature/my-feature
python -m black .
python -m ruff check . --fix
python -m pytest -q
git add .
git commit -m "Describe change"
git push
```

Before tagging a release, always run:

```bash
python -m black --check .
python -m ruff check .
python -m pytest -q
```

Do not tag a release until CI is green.

---

## Release Process

Create a new tag:

```bash
git tag v0.9.3-alpha
git push origin v0.9.3-alpha
```

GitHub Actions will create the release automatically if workflow permissions are enabled.

Recommended release rules:

```text
Never tag before CI green.
Never release from a broken merge state.
Never leave conflict markers in code.
Always run Black, Ruff, and Pytest before release.
```

---

## Roadmap

### v0.9.x-alpha

* Dashboard screenshot in README
* Dashboard polish
* Backtest chart visualizations
* Better sample data
* Real-world observation UI
* Strategy comparison table

### v1.0-alpha

* Stronger strategy module system
* Better risk engine
* Improved event/data lake architecture
* Documentation website
* Hosted dashboard demo
* Public demo video

### Future R&D

* AI research assistant
* Smart money intelligence workflows
* Portfolio research workflows
* Broker/data-provider adapters
* Advanced backtest analytics
* Strict CI workflow with mypy, bandit, and pip-audit

---

## Security

Do not commit:

```text
API keys
Telegram tokens
Broker credentials
Exchange credentials
Private wallet keys
Real trading secrets
```

Use environment variables or local `.env` files.

Read the security policy:

```text
SECURITY.md
```

---

## Contributing

Contributions are welcome for research, testing, documentation, and safe feature development.

Read:

```text
CONTRIBUTING.md
```

---

## Support

For support, setup, training, customization, or business integration, see:

```text
SUPPORT.md
```

To support development, see:

```text
DONATE.md
```

---

## Disclaimer

T is provided for research and educational purposes only.

No part of this software should be interpreted as:

* Financial advice
* Investment advice
* Trading advice
* Profit guarantee
* Risk-free system
* Live trading instruction

Markets are risky. Use responsibly.

---

## Signature

```text
━━━━━━━━━━━━━━━━━━━━
T
T Technology Research Lab
━━━━━━━━━━━━━━━━━━━━
```
