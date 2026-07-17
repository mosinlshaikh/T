# Module Ownership Map

Status: Phase 1 canonical ownership map.

## Canonical Backend Modules

| Area | Owner module | Runtime status |
|---|---|---|
| API application | `trading_os/api/app.py` | Canonical |
| API routes | `trading_os/api/routes/` | Canonical |
| Dependency access | `trading_os/api/dependencies.py` | Canonical |
| Composition root | `trading_os/orchestrator.py` | Canonical |
| Configuration | `trading_os/config.py` | Canonical |
| Binance public/spot knowledge | `trading_os/binance/`, `trading_os/connectors/` | Canonical skeleton/public-data safe |
| Market data | `trading_os/market/` | Canonical |
| Data quality | `trading_os/quality/` | Canonical |
| Intelligence | `trading_os/intelligence/` | Canonical, with explicit missing-data behavior |
| Strategy registry/catalog | `trading_os/strategies/` | Canonical, partially experimental |
| AI decision brain | `trading_os/ai/` | Canonical |
| Decision pipeline | `trading_os/pipeline/` | Canonical |
| Risk | `trading_os/risk/` | Canonical |
| Execution intent | `trading_os/execution/` | Canonical paper intent only |
| Paper execution | `trading_os/paper/` | Canonical |
| Portfolio | `trading_os/portfolio/` | Canonical |
| Trade lifecycle | `trading_os/trade/` | Canonical |
| Audit | `trading_os/audit/` | Canonical |
| Runtime supervision | `trading_os/runtime/` | Canonical |
| Notifications | `trading_os/notifications/` | Canonical skeleton, adapters not production-complete |
| Licensing | `trading_os/licensing/` | Canonical TTRL app license system |
| Learning/analytics/reports | `trading_os/learning/`, `trading_os/analytics/`, `trading_os/reports/` | Canonical paper analytics |
| Security/vault | `trading_os/security/` | Canonical policy/vault boundary; no repo secrets |
| Persistence | `trading_os/db/` | Canonical |

## Client And Deployment Modules

| Area | Owner module | Runtime status |
|---|---|---|
| Android app | `android_app/` | Canonical control-plane client |
| Railway deployment | `Dockerfile`, `Procfile`, `railway.json`, `docs/RAILWAY_DEPLOYMENT.md` | Canonical deployment path |
| CLI demo | `main.py`, `t_cli.py` | Demo/research path, not backend runtime |
| Tests | `tests/` | Canonical validation |

## Non-Canonical Or Experimental Areas

| Area | Path | Status |
|---|---|---|
| Experimental backend scaffold | `backend/` | Reference only |
| Legacy API gateway | `api/` | Non-canonical |
| Legacy/research modules | `core/`, `modules/`, `nexus/`, `enterprise/`, `realworld/`, `agents/`, `paper/`, `dashboard/`, `mobile/` | Non-canonical unless a file is explicitly imported by `trading_os` or documented later |
| Go probe | `go_services/market_probe` | Experimental, not canonical runtime |
| Rust safety guard | `rust_services/safety_guard` | Experimental, not canonical runtime |

## New Work Rule

New backend runtime features must be added under `trading_os/` unless a design document and integration test justify a separate process or language.

