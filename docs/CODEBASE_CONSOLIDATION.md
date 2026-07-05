# Codebase Consolidation

Project architect: MOSIN LIYAKAT SHAIKH, Founder / Architect of
T TECHNOLOGY RESEARCH LAB. Canonical codebase decisions in this document support
the broader TTRL AI Trading OS / T Financial Intelligence OS product direction.

## Canonical Backend

`trading_os/` is the canonical backend source of truth.

It contains the more complete Phase 1-9B implementation: API layer, persistence,
paper trading lifecycle, decision safety, analytics, reporting, Android-facing
contracts, runtime supervision, and the TTRL app license system.

## Experimental Backend

`backend/` is retained as an experimental scaffold from the newer folder-layout
phase. It is not deleted to avoid losing work, but it is not the runtime target
for the Android app or final backend checks.

## Final Entrypoints

- Backend API app: `trading_os.api.app:app`
- Backend config: `trading_os.config.TradingOSConfig`
- Persistence: `trading_os.db.repository.TradingOSRepository`
- Android integration target: backend API routes under `trading_os/api/routes/`

## Merge Policy

Useful ideas from `backend/` can be migrated into `trading_os/` module by module.
Until then, docs and Android code should point only to `trading_os/`.

## Current Status

No existing files were deleted. `backend/` is marked experimental. `trading_os/`
is the active backend for testing, API contract work, Android integration, and
future APK phases.

## Phase 10 Verification

Final review checks must use `trading_os/` as canonical. Any document or app
screen that references `backend/` must identify it as experimental unless it is
discussing historical work.
