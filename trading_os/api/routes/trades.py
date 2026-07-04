from __future__ import annotations

from dataclasses import asdict

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/open")
def open_trades() -> dict[str, object]:
    backend = get_backend()
    positions = backend.repository.list_open_positions() or [
        asdict(item) for item in backend.portfolio.open_positions.values()
    ]
    return ok(positions, "Open paper trades loaded.")


@router.get("/closed")
def closed_trades() -> dict[str, object]:
    backend = get_backend()
    positions = backend.repository.list_closed_positions() or [
        asdict(item) for item in backend.portfolio.closed_positions
    ]
    return ok(positions, "Closed paper trades loaded.")


@router.get("/journal")
def trade_journal() -> dict[str, object]:
    backend = get_backend()
    entries = backend.repository.list_trade_journal() or [
        asdict(item) for item in backend.paper_simulator.journal.entries
    ]
    return ok(entries, "Paper trade journal loaded.")


@router.get("/latest")
def latest_trade() -> dict[str, object]:
    backend = get_backend()
    persisted = backend.repository.list_trade_journal()
    entries = persisted or [asdict(item) for item in backend.paper_simulator.journal.entries]
    latest = entries[-1] if entries else None
    return ok(latest, "Latest paper trade loaded.")


@router.get("/{trade_id}")
def trade_by_id(trade_id: str) -> dict[str, object]:
    backend = get_backend()
    for position in backend.repository.list_open_positions():
        if position.get("position_id") == trade_id:
            return ok(position, "Open paper trade loaded.")
    for position in backend.repository.list_closed_positions():
        if position.get("position_id") == trade_id:
            return ok(position, "Closed paper trade loaded.")
    if trade_id in backend.portfolio.open_positions:
        return ok(asdict(backend.portfolio.open_positions[trade_id]), "Open paper trade loaded.")
    for position in backend.portfolio.closed_positions:
        if position.position_id == trade_id:
            return ok(asdict(position), "Closed paper trade loaded.")
    return ok(None, "Paper trade not found.", warnings=["Unknown trade_id."])
