from __future__ import annotations

from trading_os.api.framework import FastAPI, JSONResponse, Request
from trading_os.api.responses import fail
from trading_os.api.routes import (
    audit,
    control,
    decisions,
    licensing,
    portfolio,
    reports,
    settings,
    status,
    trades,
)


def create_app() -> FastAPI:
    app = FastAPI(title="T AI Binance Trading OS Backend API", version="0.10.0-phase10-ready")
    app.include_router(status.router)
    app.include_router(control.router)
    app.include_router(portfolio.router)
    app.include_router(trades.router)
    app.include_router(decisions.router)
    app.include_router(licensing.router)
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

    return app


app = create_app()
