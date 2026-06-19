\# T Multi-Language Architecture



\*\*Project:\*\* T

\*\*Maintainer:\*\* T Technology Research Lab

\*\*Status:\*\* Public Alpha / Research Software



```text

Research only. Not financial advice.

```



\## 1. Purpose



T is currently a Python-first financial research operating system.



This document defines the long-term developer-language architecture for T, including planned support for Go, Rust, TypeScript, and WebAssembly extension layers.



The goal is not to make the repository unnecessarily complex. The goal is to keep Python as the core while allowing future high-performance, backend, frontend, and browser-side modules to be added cleanly.



\## 2. Current Core Language



The current core language is:



```text

Python

```



Python is used for:



\* Research logic

\* Backtesting

\* Scoring utilities

\* CLI workflow

\* Streamlit dashboard

\* Tests

\* Safety guard

\* Documentation-friendly development



Python should remain the main language for the public alpha stage.



\## 3. Future Developer Language Layers



Recommended future architecture:



| Layer                 | Language     | Purpose                                                              |

| --------------------- | ------------ | -------------------------------------------------------------------- |

| Core research engine  | Python       | Backtesting, analytics, dashboard, AI research workflows             |

| SDK / API client      | Go           | Fast client tools, connector services, deployment-friendly utilities |

| Risk / scoring engine | Rust         | High-performance scoring, validation, safety-critical computation    |

| Web dashboard         | TypeScript   | Future production-grade web interface                                |

| Browser module        | Rust to WASM | Fast browser-side analytics and risk modules                         |



\## 4. Python Core



Python remains the source of truth for the current system.



Python responsibilities:



\* Data parsing

\* Alpha scoring

\* Backtest engine

\* Report generation

\* Dashboard rendering

\* Hallucination-resistant safety guard

\* Public alpha testing

\* Documentation examples



Python should stay simple, readable, and well-tested.



\## 5. Go Extension Layer



Go may be introduced later for:



\* Fast CLI tools

\* API clients

\* Data collectors

\* Lightweight backend services

\* Deployment helpers

\* Connector services



Possible future structure:



```text

sdk/

└─ go/

&#x20;  ├─ README.md

&#x20;  ├─ go.mod

&#x20;  └─ tclient.go

```



Go should not replace the Python core. It should extend T for service and integration use cases.



\## 6. Rust Extension Layer



Rust may be introduced later for:



\* High-performance risk scoring

\* Data validation

\* Safety-critical calculation

\* WebAssembly modules

\* Fast research computation

\* Memory-safe engine components



Possible future structure:



```text

engines/

└─ rust-risk/

&#x20;  ├─ Cargo.toml

&#x20;  └─ src/

&#x20;     └─ lib.rs

```



Rust should be added only when there is a real performance, safety, or portability reason.



\## 7. TypeScript Dashboard Layer



TypeScript may be introduced later if T moves beyond Streamlit into a production-grade web dashboard.



Possible use cases:



\* Dedicated frontend

\* Better UI/UX

\* Multi-language dashboard

\* Authenticated dashboard

\* API-driven analytics

\* Advanced charting



Possible future structure:



```text

web/

├─ package.json

├─ src/

└─ README.md

```



Streamlit is acceptable for public alpha. TypeScript is a future step.



\## 8. WebAssembly Layer



WebAssembly may be used later for fast browser-side modules.



Possible use cases:



\* Risk score preview

\* Local analytics

\* Browser-side validation

\* Portable computation

\* Lightweight demo modules



Possible future structure:



```text

wasm/

└─ risk-score/

```



WASM should be treated as a future optimization, not an immediate requirement.



\## 9. Design Rule



T should not add languages just to look advanced.



A new language should be added only when it provides clear value:



\* Better performance

\* Safer computation

\* Easier deployment

\* Cleaner integration

\* Better user interface

\* Wider developer adoption



\## 10. Tooling Impact



Each language adds maintenance work.



Before adding a new language layer, the repo should define:



\* Build command

\* Test command

\* Format command

\* CI workflow

\* Documentation

\* Ownership

\* Support status



\## 11. Recommended Roadmap



\### Current public alpha



```text

Python core only

Documentation for future language layers

```



\### After v0.10.0-alpha



```text

Go SDK skeleton

```



\### Later



```text

Rust risk/scoring module

TypeScript dashboard prototype

WASM analytics module

```



\## 12. Official Position



```text

T is Python-first today.

Go, Rust, TypeScript, and WASM are future extension layers.

They are planned to extend the system, not replace the Python core.

```



━━━━━━━━━━━━━━━━━━━━

T

T Technology Research Lab

━━━━━━━━━━━━━━━━━━━━



