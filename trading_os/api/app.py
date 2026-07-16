from __future__ import annotations

import asyncio
import os

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import FastAPI, JSONResponse, Request
from trading_os.api.responses import fail
from trading_os.api.routes import (
    audit,
    control,
    derivatives,
    decisions,
    learning,
    licensing,
    monitor,
    portfolio,
    reports,
    settings,
    status,
    trades,
)


def create_app() -> FastAPI:
    app = FastAPI(title="T AI Binance Trading OS Backend API", version="0.10.0-phase10-ready")
    market_stream_task: asyncio.Task[None] | None = None
    app.include_router(status.router)
    app.include_router(control.router)
    app.include_router(derivatives.router)
    app.include_router(portfolio.router)
    app.include_router(trades.router)
    app.include_router(decisions.router)
    app.include_router(learning.router)
    app.include_router(licensing.router)
    app.include_router(monitor.router)
    app.include_router(audit.router)
    app.include_router(settings.router)
    app.include_router(reports.router)

    @app.exception_handler(Exception)
    async def safe_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=fail(
                "Internal backend error.",
                errors=["Request failed safely. Check audit logs for operational details."],
            ),
        )

    if hasattr(app, "on_event"):

        @app.on_event("startup")
        async def start_public_market_stream() -> None:
            nonlocal market_stream_task
            enabled = os.getenv("T_MARKET_STREAM_ENABLED", "true").strip().lower()
            if enabled in {"0", "false", "no", "off"}:
                return
            backend = get_backend()
            if market_stream_task is None or market_stream_task.done():
                market_stream_task = asyncio.create_task(
                    backend.mini_ticker_stream.run_forever(),
                    name="ttrl-public-mini-ticker-stream",
                )
                backend.audit_logger.log(
                    "runtime_market_stream_started",
                    {
                        "source": "binance_public_miniticker_stream",
                        "public_data_only": True,
                        "live_trading_enabled": False,
                    },
                )

        @app.on_event("shutdown")
        async def stop_public_market_stream() -> None:
            nonlocal market_stream_task
            backend = get_backend()
            backend.mini_ticker_stream.stop()
            if market_stream_task is not None:
                market_stream_task.cancel()
                try:
                    await market_stream_task
                except asyncio.CancelledError:
                    pass
                market_stream_task = None
            backend.audit_logger.log(
                "runtime_market_stream_stopped",
                {
                    "source": "binance_public_miniticker_stream",
                    "public_data_only": True,
                    "live_trading_enabled": False,
                },
            )

    return app


app = create_app()
