# T

[![CI](https://github.com/mosin1982/T/actions/workflows/ci.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/ci.yml)
[![Docker Build](https://github.com/mosin1982/T/actions/workflows/docker.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/docker.yml)
[![Smoke](https://github.com/mosin1982/T/actions/workflows/smoke.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/smoke.yml)
[![Release](https://github.com/mosin1982/T/actions/workflows/release.yml/badge.svg)](https://github.com/mosin1982/T/actions/workflows/release.yml)

Open-source Financial Intelligence Operating System for market research, paper trading, backtesting, risk analysis, and smart money intelligence.

**Autonomous Financial Intelligence Platform**  
Built by **T Technology Research Lab**

> Detect. Explain. Protect.

T is a modular multi-agent intelligence platform for Crypto and Indian F&O markets. It detects smart money activity, explains market signals, protects trader capital, and supports open-source community development.

---

## Core Modules

### T Alpha Score™
A proprietary 0–100 institutional conviction score using volume anomaly, price structure, open interest, sentiment, liquidation data, and market regime.

### T Risk Shield™
Risk classification engine that suggests position risk, setup grade, stop-loss discipline, and invalidation rules.

### T Macro Guard™
Protects users from high-impact macro events such as CPI, Fed, RBI policy, jobs data, and major volatility windows.

### T Explain™
Converts every signal into beginner-friendly reasoning: what happened, why it matters, and what invalidates the setup.

### T Portfolio Doctor™
Analyzes portfolio risk, exposure, correlation, diversification, and capital protection status.

---

## Advanced Level-10 Modules

### T Copilot™
AI decision assistant for user questions such as: “Should I enter BTC now?” It answers using probability, evidence, risk, and confirmation rules.

### T Capital Preservation Engine™
Detects overexposure, drawdown risk, overtrading, and recommends position-size reduction when risk rises.

### T Institutional Radar™
Tracks ETF flows, whale transfers, funding-rate extremes, OI surges, exchange inflows/outflows, and liquidation clusters.

### T Portfolio AI™
Portfolio-level intelligence: correlation, sector exposure, hedge need, rebalancing suggestions, and risk-adjusted opportunity ranking.

### T Auto Researcher™
Generates daily/weekly market research reports with top opportunities, top risks, macro calendar, whale activity, and T Alpha rankings.

### T Reputation Score™
Tracks signal accuracy, win/loss history, false signals, and public transparency metrics.

### T Market Health Index™
Single health score for assets and markets such as BTC, ETH, NIFTY, BANKNIFTY.

### T Opportunity Scanner™
Ranks best trade setups across crypto and Indian markets using multi-factor scoring.

### T Learning Mode™
Teaches beginners why a signal triggered and how smart money behavior is interpreted.

### T Research Vault™
Stores market reports, strategy papers, backtests, alpha research, and community knowledge.

---

## Multi-Agent Architecture

- **T Quant** — market data, volume anomaly, OI, price structure
- **T Oracle** — sentiment, news, macro intelligence
- **T Broadcaster** — Telegram alerts and premium message formatting
- **T Copilot** — user-facing AI decision assistant
- **T Researcher** — daily reports and institutional summaries
- **T Risk Engine** — risk guardrails and capital protection

---

## Donation / Community Support

If T helps you make better market decisions, consider supporting development.

### UPI
`tmps8346991530153183@slc`

### USDT TRC20
`TLFLEDbN47bSBkWeqZzMNgkrzRK64RHbVn`

### Binance UID
`475627577`

Funds support infrastructure, APIs, research, AI development, and open-source maintenance.

---

## CI/CD

This repository includes production-ready CI/CD:

- Python linting with Ruff
- Formatting checks with Black
- Type checks with MyPy
- Unit tests with Pytest
- Security scan with Bandit
- Dependency audit with pip-audit
- Docker image build validation
- Release workflow template
- Deployment templates for Docker, Render, Railway, and VPS

---

## License

This project is source-available under **T License v1.0**.  
Personal, educational, and research use is allowed. Commercial use requires written permission from T Technology Research Lab.


---

## Public Release Status

Current status: `v0.4.0-alpha`

T is under active development. It is not a guaranteed-profit system and must not be treated as financial advice.

The first public GitHub release should focus on:

- Education
- Research
- Paper trading
- Backtesting
- Risk management
- Open-source collaboration

Live trading should only be considered after extensive validation.

---

## Why Donations Are Optional

T is free for personal, educational, and research use.

If this project helps you learn, build, test strategies, or save development time, you may support future development through the donation methods in `DONATE.md`.

No donation is required to use the community edition.

## 60-Second Working Demo

```bash
pip install -r requirements.txt
python t_cli.py demo
```

## Real-World Public Market Observation

```bash
cp .env.example .env
python t_cli.py real-binance --symbol btcusdt --threshold 3.0
```

Real-world mode observes public Binance market data only. It does not place trades.



## Run Backtest

```bash
python t_cli.py backtest
```

This generates a proof-oriented research report with trades, win rate, profit factor, drawdown, fees, and slippage.

---

## Full Platform Modules Included

This repository now includes foundations for:

- T Demo Mode
- T Real-World Observation Mode
- T Paper Trading Mode
- T Backtest Engine
- T Event Sourcing
- T Nexus Graph
- T Data Lake
- T Mission Control
- T Validation Center
- T Benchmark Engine
- T Data Quality Engine
- T API Gateway
- T SDK
- T Plugin System
- Governance ADR/RFC docs
- GitHub publish checklist

## Platform Status

Current recommended public tag: `v0.8.0-alpha`

T is research-only. It does not guarantee profit and does not execute live trades by default.
