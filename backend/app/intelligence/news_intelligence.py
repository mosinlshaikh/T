from __future__ import annotations


def news_signal(items: list[dict[str, object]] | None) -> dict[str, object]:
    if not items:
        return {"signal": "SKIP", "missing_data": ["news"], "reason": "No news evidence."}
    valid = [item for item in items if item.get("source") and item.get("timestamp")]
    if not valid:
        return {"signal": "SKIP", "missing_data": ["news_source_timestamp"]}
    return {"signal": "HOLD", "evidence": valid}
