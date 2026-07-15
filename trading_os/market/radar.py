from __future__ import annotations

from typing import Any


def radar_score(row: dict[str, Any]) -> float:
    quote_volume = float(row.get("quote_volume", 0.0) or 0.0)
    move = abs(float(row.get("price_change_pct", 0.0) or 0.0))
    volatility = float(row.get("volatility_pct", 0.0) or 0.0)
    trade_count = float(row.get("trade_count", 0.0) or 0.0)
    volume_score = min(quote_volume / 25_000_000, 1.0) * 40
    move_score = min(move / 12, 1.0) * 25
    volatility_score = min(volatility / 18, 1.0) * 20
    activity_score = min(trade_count / 75_000, 1.0) * 15
    return round(volume_score + move_score + volatility_score + activity_score, 4)


def rank_market_radar_rows(
    rows: list[dict[str, Any]],
    limit: int = 30,
    min_quote_volume: float = 50_000,
    min_trade_count: int = 10,
) -> list[dict[str, object]]:
    safe_limit = min(max(int(limit), 1), 80)
    candidates: list[dict[str, object]] = []
    for row in rows:
        quote_volume = float(row.get("quote_volume", 0.0) or 0.0)
        trade_count = int(row.get("trade_count", 0) or 0)
        if quote_volume < min_quote_volume or trade_count < min_trade_count:
            continue
        score = radar_score(row)
        candidates.append(
            {
                **row,
                "radar_score": score,
                "reason": (
                    f"volume={round(quote_volume, 2)}; "
                    f"move={row.get('price_change_pct')}%; "
                    f"volatility={row.get('volatility_pct')}%"
                ),
                "deep_scan_recommended": score >= 12,
            }
        )
    return sorted(candidates, key=lambda item: float(item["radar_score"]), reverse=True)[
        :safe_limit
    ]
