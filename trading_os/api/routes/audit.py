from __future__ import annotations

from trading_os.api.dependencies import latest_audit_events
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok, redact_sensitive

router = APIRouter(prefix="/audit", tags=["audit"])


def _events(limit: int = 100, event_type: str | None = None) -> list[dict[str, object]]:
    return redact_sensitive(latest_audit_events(limit=limit, event_type=event_type))


@router.get("/latest")
def latest() -> dict[str, object]:
    return ok(_events(limit=25), "Latest audit events loaded.")


@router.get("/events")
def events() -> dict[str, object]:
    return ok(_events(limit=100), "Audit events loaded.")


@router.get("/errors")
def errors() -> dict[str, object]:
    error_events = [
        item for item in _events(limit=100) if "error" in str(item.get("event_type", "")).lower()
    ]
    return ok(error_events, "Audit error events loaded.")


@router.get("/security")
def security() -> dict[str, object]:
    wanted = {"config_validation_result", "secret_availability_status", "api_readiness_result"}
    return ok(
        [item for item in _events(limit=100) if item.get("event_type") in wanted],
        "Security audit events loaded.",
    )


@router.get("/runtime")
def runtime() -> dict[str, object]:
    wanted = {"runtime_heartbeat", "supervisor_state_change", "reconnect_attempt"}
    return ok(
        [item for item in _events(limit=100) if item.get("event_type") in wanted],
        "Runtime audit events loaded.",
    )
