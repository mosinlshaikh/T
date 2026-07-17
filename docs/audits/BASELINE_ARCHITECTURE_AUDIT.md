# Phase 0 Baseline Architecture Audit

Date: 2026-07-17

Scope: repository forensics and baseline validation for the TTRL AI Trading OS repository. This report records verified findings only. The system remains paper-trading only; no live Binance order placement or withdrawal capability was enabled or tested.

## Executive Baseline

- Canonical backend runtime: `trading_os.api.app:app`.
- Canonical backend package: `trading_os/`.
- Experimental backend scaffold: `backend/`, already marked as reference-only in `backend/README.md`.
- Android control-plane source: `android_app/`.
- Go component status: `go_services/market_probe` compiles, but has no tests.
- Rust component status: `rust_services/safety_guard` exists, but Rust/Cargo is not installed in the local environment.
- Current local dirty file before this audit: `DONATE.md`.
- Existing repository root contains a debug APK artifact: `TTRL_AI_TRADING_OS_DEBUG.apk`.

## Canonical Runtime Evidence

| Evidence | Verified file | Finding |
|---|---|---|
| Docker startup | `Dockerfile` | Starts `python -m uvicorn trading_os.api.app:app --host 0.0.0.0 --port ${PORT:-8000}`. |
| Railway process | `Procfile` | Starts `python -m uvicorn trading_os.api.app:app --host 0.0.0.0 --port ${PORT:-8000}`. |
| Railway health path | `railway.json` | Healthcheck path is `/status/health`. |
| FastAPI app factory | `trading_os/api/app.py` | Defines `create_app()` and module-level `app = create_app()`. |
| Backend composition root | `trading_os/orchestrator.py` | Defines `TradingOSBackend`, wiring config, DB, audit, risk, pipeline, paper simulator, runtime, and market stream components. |
| Experimental backend marker | `backend/README.md` | States canonical backend is `trading_os/` and `backend/` is retained for reference only. |
| Legacy API gateway | `api/server.py` | Separate older gateway title `T API Gateway`, not referenced by Docker/Railway canonical runtime. |

## Repository Inventory

- Total files discovered by `rg --files`: `431`.
- Python files scanned for import graph across `trading_os`, `backend`, `api`, `core`, `modules`, `nexus`, `enterprise`, `realworld`, and `agents`: `214`.
- Top-level folders include both canonical and non-canonical areas: `trading_os/`, `backend/`, `api/`, `core/`, `modules/`, `nexus/`, `enterprise/`, `realworld/`, `agents/`, `android_app/`, `go_services/`, and `rust_services/`.

## Import Graph Baseline

Command summary:

```powershell
python -B <AST import graph script>
```

Result:

- Internal modules with imports: `85`.
- `trading_os` internal outbound import edges: `253`.
- `trading_os` internal inbound import edges: `253`.
- `backend` internal outbound import edges: `14`.
- `backend` internal inbound import edges: `14`.
- `trading_os` imports into legacy/non-canonical packages: `0`.
- Circular imports found: `1`, limited to experimental backend:
  - `backend.app.decision.ai_decision_brain -> backend.app.decision.zero_hallucination_engine -> backend.app.decision.ai_decision_brain`

Interpretation: canonical `trading_os/` is currently isolated from the experimental backend scaffold at import level. The experimental `backend/` package has at least one circular import and must not be treated as production.

## Duplicate Responsibility Findings

| Responsibility | Canonical location | Duplicate/legacy location | Finding |
|---|---|---|---|
| Backend API | `trading_os/api/` | `api/server.py`, `backend/app/api/` | Canonical runtime uses `trading_os/api/app.py`; other API folders are legacy/experimental. |
| Persistence | `trading_os/db/` | `trading_os/database/`, `backend/app/database/` | `trading_os/db/` is active via `TradingOSRepository`; `trading_os/database/` and `backend/app/database/` need ownership/deprecation clarification in Phase 1. |
| Decision pipeline | `trading_os/pipeline/decision_to_trade.py` | `backend/app/decision/` | Canonical pipeline is under `trading_os`; experimental backend has circular decision imports. |
| Strategy registry | `trading_os/strategies/registry.py` | `backend/app/strategy/` | Canonical runtime wires `StrategyRegistry.with_default_placeholders()` from `trading_os`. |
| Android client | `android_app/` | `mobile/` | Android source currently lives in `android_app/`; `mobile/` is documentation/legacy unless proven otherwise. |

## Placeholder And Scaffold Findings

Verified placeholder markers:

- `trading_os/orchestrator.py`: uses `StrategyRegistry.with_default_placeholders()`.
- `trading_os/intelligence/whale_intelligence_v1.py`: contains `exchange_activity_signal: "placeholder"`.
- `trading_os/notifications/engine.py`: abstract adapter dispatch raises `NotImplementedError`.
- `trading_os/security/api_key_vault.py`: vault design placeholder and external secret storage methods raise `NotImplementedError`.
- `trading_os/strategies/catalog.py`: some derivatives/options entries are explicitly paper/research placeholders.
- `backend/app/*`: multiple `placeholder` strings in experimental backend scaffold.

Interpretation: placeholders exist but are mostly documented as scaffold/private-boundary placeholders. They must not be represented as production-complete. Critical production path must continue to fail closed when these data sources are unavailable.

## Baseline Checks

| Check | Command | Result |
|---|---|---|
| Python tests | `python -B -m pytest -q` | PASS: `95` tests passed. |
| Ruff lint | `python -B -m ruff check .` | PASS. |
| Black format | `python -B -m black --check .` | PASS: `286` files unchanged. |
| Python package dependency consistency | `python -B -m pip check` | PASS: no broken requirements found. |
| API import smoke | `python -B -c "import trading_os.api.app ..."` | PASS: app title loaded and `TradingOSBackend` imported. |
| CLI smoke | `python -B t_cli.py demo` | PASS, but demo prints idealized sample paper output and must remain labelled research/demo. |
| Mypy | `python -B -m mypy trading_os tests` | NOT RUN: local Python environment has no `mypy` module installed. |
| Bandit | `python -B -m bandit -q -r trading_os backend api main.py` | NOT RUN: local Python environment has no `bandit` module installed. |
| pip-audit | `python -B -m pip_audit` | NOT RUN: local Python environment has no `pip_audit` module installed. |
| Docker build | `docker build -t ttrl-baseline:phase0 .` | NOT RUN: Docker Desktop Linux engine/daemon unavailable. |
| Go tests | `go test ./...` in `go_services/market_probe` | PASS: module compiles, `[no test files]`. |
| Rust tests | `cargo test` in `rust_services/safety_guard` | NOT RUN: `cargo` command not available. |
| Android debug build | `.\gradlew.bat --no-daemon :app:assembleDebug` | PASS; debug APK exists at `android_app/app/build/outputs/apk/debug/app-debug.apk`. |
| FastAPI TestClient smoke | `from fastapi.testclient import TestClient` | NOT RUN: local Starlette TestClient requires missing `httpx2`. |
| Local uvicorn default DB smoke | local `uvicorn trading_os.api.app:app` with file-backed default DB | PASS: `/status/health`, `/status/binance-readiness`, `/portfolio/open-positions`, `/monitor/paper-scan-summary` returned HTTP 200 and success true. |
| Local uvicorn in-memory DB smoke | `T_DATABASE_URL=sqlite:///:memory:` | FAIL: startup fails with `sqlite3.OperationalError: no such table: records`. |

## API Startup Findings

Default file-backed SQLite startup passes. In-memory SQLite startup fails because `SQLiteStorage` opens a new SQLite connection for each operation, and `:memory:` databases are connection-local.

Verified files:

- `trading_os/db/storage.py`: `SQLiteStorage.initialize()` creates schema using one connection, while `save_record()` opens another connection.
- `trading_os/db/repository.py`: audit save path calls `storage.save_record()`.
- `trading_os/api/app.py`: startup event logs `runtime_market_stream_started`; that audit write triggers the missing `records` table when the DB is in-memory.

Impact:

- Production/default file-backed SQLite works.
- Isolated in-memory smoke tests are unreliable until storage supports a shared in-memory connection or tests use a temporary file database.

## Safety Baseline

Verified safety defaults:

- `trading_os/config.py` forces `enable_live_trading=False` in `TradingOSConfig.from_env()`.
- `trading_os/config.py` forces `allow_withdraw_permissions=False`.
- `TradingOSConfig.assert_safe()` raises if live trading, manual live unlock, or withdrawal support becomes true.
- Paper pipeline no-data sample returned:
  - action: `SKIP`
  - status: `REJECTED_BY_ZERO_HALLUCINATION`
  - reason: `Missing required evidence: market_tick`

Measured command:

```powershell
python -B <pipeline no-data timing script>
```

Result:

- API import time: `2279.44 ms`.
- Backend construction time: `27.67 ms`.
- No-data pipeline latency: `418.88 ms`.
- No-data action/status: `SKIP` / `REJECTED_BY_ZERO_HALLUCINATION`.

## Secret Scan Baseline

Lightweight string scan over `trading_os`, `android_app/app/src`, `backend`, `api`, `docs`, and `.env.example` found environment variable names but no literal private key text.

Findings:

- `BINANCE_API_KEY` appears as placeholder/env-var name in `.env.example`, `trading_os/config.py`, and security modules.
- `BINANCE_API_SECRET` appears as placeholder/env-var name in `.env.example`, `trading_os/config.py`, and security modules.
- `TTRL_ADMIN_TOKEN` appears as placeholder/env-var name in `.env.example`, docs, and `trading_os/api/routes/licensing.py`.
- `PRIVATE KEY` text count: `0`.

Limitations:

- Full entropy-based secret scan was not run because `gitleaks` was not available in this local baseline.
- The scan output included `__pycache__` paths; generated caches should be excluded from formal CI secret scans.

## Android Baseline

Verified:

- Android application package: `com.ttechnologyresearchlab.tradingos`.
- Debug build succeeded.
- Debug APK path: `android_app/app/build/outputs/apk/debug/app-debug.apk`.
- Debug APK size at baseline: `17,056,575` bytes.
- Android source references backend API only through `android_app/app/src/main/java/com/ttechnologyresearchlab/tradingos/network/BackendApiClient.kt`.
- Source contains paper-mode and live-disabled labels.

Not verified in this phase:

- Automated Android UI contract test suite.
- Certificate pinning.
- Secure token storage.

## Go/Rust Baseline

Go:

- `go_services/market_probe/go.mod` exists.
- `go test ./...` passes with `[no test files]`.
- This component is not wired into canonical `trading_os` runtime.

Rust:

- `rust_services/safety_guard/Cargo.toml` exists.
- `cargo test` could not run because Cargo is not installed locally.
- This component is not wired into canonical `trading_os` runtime.

## Known Baseline Gaps

1. Multiple non-canonical folders exist and need formal ownership/deprecation docs: `api/`, `backend/`, `core/`, `modules/`, `nexus/`, `enterprise/`, `realworld/`, and `agents/`.
2. `trading_os/db/` and `trading_os/database/` create a naming ambiguity.
3. Experimental `backend/app/decision` contains a circular import.
4. Strategy registry still uses placeholder strategy naming and should be separated into implemented, experimental, and private-boundary strategy classes.
5. `SQLiteStorage` does not support `sqlite:///:memory:` across multiple connections.
6. Critical security tools are listed in `requirements.txt` but missing in the active local Python 3.14 interpreter used by this shell.
7. Docker cannot be validated locally until Docker Desktop Linux engine is running.
8. Rust cannot be validated locally until Cargo is installed.
9. FastAPI TestClient contract tests cannot run until the local environment provides the required `httpx2` dependency expected by Starlette.
10. CI currently checks Ruff, Black, Pytest, Docker, and smoke, but not mypy, bandit, pip-audit, secret scanning, Android build, Go tests, Rust tests, or import-boundary checks.

## Commands Needed To Reproduce Baseline

```powershell
cd "C:\Users\MOSIN L. SHAIKH\OneDrive\Desktop\T"
python -B -m pytest -q
python -B -m ruff check .
python -B -m black --check .
python -B -m pip check
python -B t_cli.py demo
python -B -c "import trading_os.api.app as a; print(a.app.title)"
docker build -t ttrl-baseline:phase0 .
cd go_services\market_probe; go test ./...
cd ..\..\rust_services\safety_guard; cargo test
cd ..\..\android_app; $env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'; .\gradlew.bat --no-daemon :app:assembleDebug
```

## Phase 1 Recommendations

The next phase should not rewrite the system. It should make the existing architecture unambiguous and enforce it:

1. Add `docs/architecture/CANONICAL_ARCHITECTURE.md`.
2. Add `docs/architecture/MODULE_OWNERSHIP_MAP.md`.
3. Add `docs/architecture/LEGACY_AND_DEPRECATED_MODULES.md`.
4. Add an import-boundary CI check proving `trading_os/` does not import legacy packages.
5. Resolve or document `trading_os/db` versus `trading_os/database`.
6. Mark experimental `backend/app` cycle as non-canonical, or fix it if that scaffold is retained for tests.
7. Add a safe regression test or documented limitation for in-memory SQLite behavior.

