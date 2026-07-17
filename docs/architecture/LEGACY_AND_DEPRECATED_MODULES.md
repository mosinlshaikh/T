# Legacy And Deprecated Modules

Status: registry for non-canonical code paths.

This file prevents accidental activation of older scaffolds. It does not delete code.

## Reference-Only Backend Scaffold

Path: `backend/`

Status: experimental/reference-only.

Reason:

- It overlaps with `trading_os/` across API, Binance, market, decision, strategy, risk, execution, database, audit, and security responsibilities.
- Phase 0 import graph found one circular import inside `backend/app/decision`.
- `backend/README.md` already marks it as experimental.

Rule:

- Do not point Docker, Railway, Android, or docs API contracts to `backend/`.
- Migrate useful modules into `trading_os/` only after review and tests.

## Legacy API Gateway

Path: `api/server.py`

Status: legacy/demo.

Reason:

- It defines an older `T API Gateway`.
- It is not used by Docker, Railway, or Android.

Rule:

- Do not add new Android/backend contracts here.

## Legacy Research/Scaffold Roots

Paths:

- `agents/`
- `core/`
- `dashboard/`
- `enterprise/`
- `mobile/`
- `modules/`
- `nexus/`
- `paper/`
- `realworld/`

Status: non-canonical unless a future audit promotes a specific file.

Rule:

- `trading_os/` must not import from these roots.
- A CI import-boundary check prevents accidental dependency.

## Persistence Ambiguity

Paths:

- Canonical: `trading_os/db/`
- Legacy/skeleton: `trading_os/database/`
- Experimental: `backend/app/database/`

Status:

- New persistence work must use `trading_os.db`.
- `trading_os/database` remains a compatibility/skeleton namespace until all references are audited.
- `backend/app/database` belongs to the experimental backend scaffold.

## Cross-Language Experimental Services

Paths:

- `go_services/market_probe`
- `rust_services/safety_guard`

Status:

- Not canonical runtime components.
- Go probe compiles locally.
- Rust tests were not run in Phase 0 because Cargo was unavailable.

Promotion requirements:

- Typed protocol.
- Health endpoint.
- Timeout and retry policy.
- Circuit breaker.
- Integration test with `trading_os`.
- Fallback behavior.
- Documentation and CI coverage.

