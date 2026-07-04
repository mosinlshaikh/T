from __future__ import annotations

from datetime import datetime, timezone


def heartbeat() -> dict[str, object]:
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
