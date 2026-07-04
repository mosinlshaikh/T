# Railway Deployment

1. Push repo to GitHub.
2. Import project in Railway.
3. Add environment variables from `.env.example`.
4. Railway should detect root `railway.json` and `Dockerfile`.
5. Health check path: `/status/health`.

Use `TRADING_MODE=paper`, `LIVE_TRADING_ENABLED=false`,
`MANUAL_LIVE_UNLOCK=false`, and `BINANCE_WITHDRAWALS_SUPPORTED=false`.

See `docs/RAILWAY_DEPLOYMENT.md` for the full checklist.
