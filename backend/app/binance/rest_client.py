from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BinanceRestClient:
    base_url: str = "https://api.binance.com"
    rate_limit_per_minute: int = 1200

    def public_market_snapshot(self, symbol: str) -> dict[str, object]:
        return {"symbol": symbol.upper(), "source": "public_rest_placeholder"}

    def signed_request(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Signed/private Binance requests are disabled in this foundation.")
