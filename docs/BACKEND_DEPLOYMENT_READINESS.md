# Backend Deployment Readiness

This document covers the safe deployment path for the canonical TTRL AI Trading
OS backend.

## Canonical Runtime

- Backend source of truth: `trading_os/`
- FastAPI app: `trading_os.api.app:app`
- Local API port: `8000`
- Android app target: backend HTTP API only
- Experimental folder: `backend/`

The `backend/` folder is retained as an experimental scaffold. Production and
APK integration should use `trading_os.api.app:app`.

## Required Safe Environment

Use placeholders only. Do not commit `.env`.

```env
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
MANUAL_LIVE_UNLOCK=false
BINANCE_WITHDRAWALS_SUPPORTED=false
T_DATABASE_URL=sqlite:///data/trading_os.sqlite3
T_AUDIT_LOG_PATH=data/audit/trading_os_audit.jsonl
TTRL_ADMIN_TOKEN=
```

`TTRL_ADMIN_TOKEN` is required only for owner/admin license generation routes.
It must be created on the server as a private environment variable. It must not
be hardcoded in source code, Android code, docs, screenshots, logs, or tests.

## Local Backend Command

```bash
python -m uvicorn trading_os.api.app:app --host 127.0.0.1 --port 8000
```

Windows helper:

```powershell
.\scripts\start_backend.ps1 -HostName 127.0.0.1 -Port 8000
```

Linux/macOS helper:

```bash
bash scripts/start_backend.sh
```

Health check:

```bash
curl http://127.0.0.1:8000/status/health
```

Cross-platform safety health check:

```bash
python scripts/check_backend_health.py http://127.0.0.1:8000
```

Expected safety state:

- `mode`: `paper`
- `live_trading_enabled`: `false`
- `withdraw_permissions_supported`: `false`
- Binance readiness: `READY_FOR_PAPER` or safe blocked state

## Docker Command

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/status/health
```

Docker runs:

```bash
python -m uvicorn trading_os.api.app:app --host 0.0.0.0 --port 8000
```

## Render/Railway Start Command

Use:

```bash
python -m uvicorn trading_os.api.app:app --host 0.0.0.0 --port $PORT
```

Platforms that support a `Procfile` can use the included `Procfile`.

Railway-specific deployment is documented in
[`docs/RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md). The repository includes
`railway.json` with `/status/health` configured as the deployment health check.

Add environment variables from `.env.example`, keeping live trading disabled and
withdrawals unsupported.

## Android Connection

For local USB testing:

```bash
adb reverse tcp:8000 tcp:8000
```

Then set or use backend URL:

```text
http://127.0.0.1:8000
```

For deployed backend, use the HTTPS URL in the Android Settings screen.

## License Flow

Owner/admin backend generates TTRL app license keys. The Android app only
validates keys through:

```text
POST /license/validate
```

TTRL license keys are not Binance API keys. Binance API keys must still be
created by the user inside Binance and handled separately through the backend
vault design. No API key submission endpoint exists in the APK.

## Deployment Safety Checklist

- `.env` is gitignored.
- No Binance credentials in source.
- No admin token in source.
- No withdrawal support.
- No live trading enable endpoint.
- Paper mode remains default.
- Android APK talks only to backend API.
- License generation routes require admin token.
- App license validation does not expose full keys after validation.
- `/status/health` returns safe paper-mode state.

## Current Limitation

This is a paper-mode backend deployment foundation. It is not a commercial live
trading service and does not place real Binance orders.
