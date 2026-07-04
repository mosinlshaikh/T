from __future__ import annotations

from dataclasses import asdict

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


def _portfolio_summary() -> dict[str, object]:
    backend = get_backend()
    persisted = backend.repository.get_latest_portfolio_snapshot()
    wallet = backend.portfolio.wallet_snapshot()
    return {
        "wallet": persisted or asdict(wallet),
        "open_positions": len(backend.portfolio.open_positions),
        "closed_positions": len(backend.portfolio.closed_positions),
        "exposure": backend.portfolio.exposure(),
        "available_capital": backend.portfolio.available_capital(),
        "daily_pnl": backend.portfolio.daily_pnl(),
        "drawdown_pct": backend.portfolio.drawdown_pct(),
        "mode": "paper",
    }


@router.get("/summary")
def summary() -> dict[str, object]:
    return ok(_portfolio_summary(), "Paper portfolio summary loaded.")


@router.get("/wallet")
def wallet() -> dict[str, object]:
    backend = get_backend()
    persisted = backend.repository.get_latest_portfolio_snapshot()
    return ok(persisted or asdict(backend.portfolio.wallet_snapshot()), "Paper wallet loaded.")


@router.get("/open-positions")
def open_positions() -> dict[str, object]:
    backend = get_backend()
    positions = backend.repository.list_open_positions() or [
        asdict(item) for item in backend.portfolio.open_positions.values()
    ]
    return ok(positions, "Open paper positions loaded.")


@router.get("/closed-positions")
def closed_positions() -> dict[str, object]:
    backend = get_backend()
    positions = backend.repository.list_closed_positions() or [
        asdict(item) for item in backend.portfolio.closed_positions
    ]
    return ok(positions, "Closed paper positions loaded.")


@router.get("/pnl")
def pnl() -> dict[str, object]:
    backend = get_backend()
    return ok(
        {
            "realized_pnl": backend.portfolio.realized_pnl,
            "unrealized_pnl": backend.portfolio.unrealized_pnl({}),
            "daily_pnl": backend.portfolio.daily_pnl(),
            "drawdown_pct": backend.portfolio.drawdown_pct(),
        },
        "Paper PnL loaded.",
    )


@router.get("/exposure")
def exposure() -> dict[str, object]:
    backend = get_backend()
    return ok(
        {
            "exposure": backend.portfolio.exposure(),
            "available_capital": backend.portfolio.available_capital(),
            "reserve_capital": backend.portfolio.reserved_capital,
        },
        "Paper exposure loaded.",
    )
