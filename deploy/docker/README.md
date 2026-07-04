# Docker Deployment

```bash
cp .env.example .env
docker compose up --build -d
```

Health check:

```bash
curl http://localhost:8000/status/health
```

Or:

```bash
python scripts/check_backend_health.py http://localhost:8000
```

This starts the canonical backend API: `trading_os.api.app:app`.
Live trading remains disabled and withdrawals are unsupported.
