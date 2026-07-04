#!/usr/bin/env bash
set -euo pipefail

HOST_NAME="${HOST_NAME:-127.0.0.1}"
PORT="${PORT:-8000}"

export TRADING_MODE="${TRADING_MODE:-paper}"
export LIVE_TRADING_ENABLED="false"
export MANUAL_LIVE_UNLOCK="false"
export BINANCE_WITHDRAWALS_SUPPORTED="false"

python -m uvicorn trading_os.api.app:app --host "$HOST_NAME" --port "$PORT"
