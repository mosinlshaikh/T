from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    url = f"{base_url}/status/health"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    data = payload.get("data") or {}
    result = {
        "ok": bool(payload.get("success")),
        "mode": data.get("mode"),
        "live_trading_enabled": data.get("live_trading_enabled"),
        "withdraw_permissions_supported": data.get("withdraw_permissions_supported"),
        "readiness": (data.get("binance_readiness_status") or {}).get("status"),
    }
    print(json.dumps(result, sort_keys=True))

    if result["mode"] != "paper":
        return 2
    if result["live_trading_enabled"] is not False:
        return 3
    if result["withdraw_permissions_supported"] is not False:
        return 4
    return 0 if result["ok"] else 5


if __name__ == "__main__":
    raise SystemExit(main())
