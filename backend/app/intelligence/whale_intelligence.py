from __future__ import annotations


def whale_signal(trades: list[dict[str, object]] | None) -> dict[str, object]:
    if not trades:
        return {"signal": "SKIP", "missing_data": ["whale_trades"], "reason": "No whale data."}
    return {"signal": "HOLD", "evidence": trades, "reason": "Whale data present; no fake claim."}
