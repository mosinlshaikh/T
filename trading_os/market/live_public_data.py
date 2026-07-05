from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from trading_os.ai.decision_types import EvidenceItem, EvidenceType
from trading_os.intelligence.news_risk_intelligence import NewsItem
from trading_os.intelligence.whale_intelligence_v1 import WhaleTrade
from trading_os.market.candle_engine import Candle
from trading_os.market.market_data_engine import RestMarketSnapshot
from trading_os.market.order_book_engine import OrderBookLevel, OrderBookSnapshot
from trading_os.market.timeframes import Timeframe, normalize_timeframe
from trading_os.pipeline.decision_to_trade import PipelineInput


BINANCE_PUBLIC_BASE_URL = "https://api.binance.com"
BINANCE_ANNOUNCEMENT_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class LiveMarketBundle:
    symbol: str
    timeframe: Timeframe
    snapshot: RestMarketSnapshot
    candles: list[Candle]
    order_book: OrderBookSnapshot
    whale_trades: list[WhaleTrade]
    news_items: list[NewsItem]
    evidence: list[EvidenceItem]
    warnings: list[str]


@dataclass
class BinancePublicMarketDataClient:
    """Public market-data reader.

    This client uses only unauthenticated public endpoints. It never reads,
    stores, signs, or sends Binance API keys and cannot place orders.
    """

    base_url: str = BINANCE_PUBLIC_BASE_URL
    timeout_seconds: int = 8

    def fetch_bundle(
        self,
        symbol: str = "BTCUSDT",
        timeframe: str | Timeframe = Timeframe.FIVE_MINUTES,
        candle_limit: int = 80,
        order_book_limit: int = 50,
        trade_limit: int = 80,
    ) -> LiveMarketBundle:
        symbol = symbol.upper()
        tf = normalize_timeframe(timeframe)
        warnings: list[str] = []

        ticker = self._get_json("/api/v3/ticker/24hr", {"symbol": symbol})
        snapshot = RestMarketSnapshot(
            symbol=symbol,
            price=float(ticker["lastPrice"]),
            volume_24h=float(ticker["volume"]),
            event_time_ms=int(ticker.get("closeTime", 0) or 0),
            source="binance_public_ticker_24hr",
        )

        candles = [
            self._candle_from_kline(symbol, tf, item)
            for item in self._get_json(
                "/api/v3/klines",
                {"symbol": symbol, "interval": tf.value, "limit": max(candle_limit, 5)},
            )
        ]

        depth = self._get_json(
            "/api/v3/depth",
            {"symbol": symbol, "limit": order_book_limit},
        )
        order_book = OrderBookSnapshot(
            symbol=symbol,
            bids=[
                OrderBookLevel(price=float(price), quantity=float(quantity))
                for price, quantity in depth.get("bids", [])
            ],
            asks=[
                OrderBookLevel(price=float(price), quantity=float(quantity))
                for price, quantity in depth.get("asks", [])
            ],
            event_time_ms=int(snapshot.event_time_ms),
            last_update_id=int(depth.get("lastUpdateId", 0) or 0),
            source="binance_public_depth",
        )

        whale_trades = [
            self._whale_trade_from_agg(symbol, item)
            for item in self._get_json(
                "/api/v3/aggTrades",
                {"symbol": symbol, "limit": trade_limit},
            )
        ]

        news_items: list[NewsItem] = []
        try:
            news_items = self.fetch_binance_announcements(symbol)
        except Exception:
            warnings.append("News source unavailable; news risk signal may SKIP.")

        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.MARKET_TICK,
                source=snapshot.source,
                summary=(
                    f"{symbol} public ticker price={snapshot.price}; "
                    f"24h_volume={snapshot.volume_24h}"
                ),
                confidence=1.0,
                timestamp=utc_now(),
                payload={
                    "symbol": symbol,
                    "price": snapshot.price,
                    "volume_24h": snapshot.volume_24h,
                    "source": snapshot.source,
                },
            ),
            EvidenceItem(
                evidence_type=EvidenceType.MARKET_SNAPSHOT,
                source="binance_public_bundle",
                summary=(
                    f"candles={len(candles)}; order_book_bids={len(order_book.bids)}; "
                    f"order_book_asks={len(order_book.asks)}; whale_trades={len(whale_trades)}; "
                    f"news_items={len(news_items)}"
                ),
                confidence=1.0,
                timestamp=utc_now(),
            ),
        ]
        return LiveMarketBundle(
            symbol=symbol,
            timeframe=tf,
            snapshot=snapshot,
            candles=candles,
            order_book=order_book,
            whale_trades=whale_trades,
            news_items=news_items,
            evidence=evidence,
            warnings=warnings,
        )

    def build_pipeline_input(
        self,
        bundle: LiveMarketBundle,
        account_balance: float,
        current_exposure: float,
        trade_notional_usdt: float = 50.0,
    ) -> PipelineInput:
        price = bundle.snapshot.price
        quantity = round(max(trade_notional_usdt, 10.0) / price, 8)
        stop_loss = round(price * 0.99, 8)
        take_profit = round(price * 1.015, 8)
        return PipelineInput(
            symbol=bundle.symbol,
            timeframe=bundle.timeframe,
            market_price=price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            account_balance=account_balance,
            current_exposure=current_exposure,
            candles=bundle.candles,
            order_book=bundle.order_book,
            whale_trades=bundle.whale_trades,
            news_items=bundle.news_items,
        )

    def fetch_binance_announcements(self, symbol: str, limit: int = 5) -> list[NewsItem]:
        asset = symbol.upper().replace("USDT", "")
        payload = self._get_url_json(
            BINANCE_ANNOUNCEMENT_URL,
            {
                "catalogId": 48,
                "pageNo": 1,
                "pageSize": limit,
            },
        )
        articles = (
            payload.get("data", {})
            .get("articles", [])
            if isinstance(payload, dict)
            else []
        )
        items: list[NewsItem] = []
        for article in articles[:limit]:
            title = str(article.get("title", "")).strip()
            release_ms = int(article.get("releaseDate", 0) or 0)
            if not title:
                continue
            if asset and asset not in title.upper() and "BINANCE" not in title.upper():
                continue
            timestamp = (
                datetime.fromtimestamp(release_ms / 1000, timezone.utc).isoformat()
                if release_ms
                else utc_now()
            )
            code = str(article.get("code", "")).strip()
            items.append(
                NewsItem(
                    headline=title,
                    source="binance_public_announcements",
                    timestamp=timestamp,
                    url=f"https://www.binance.com/en/support/announcement/{code}" if code else "",
                )
            )
        return items

    def _get_json(self, path: str, params: dict[str, Any]) -> Any:
        return self._get_url_json(f"{self.base_url}{path}", params)

    def _get_url_json(self, url: str, params: dict[str, Any]) -> Any:
        full_url = f"{url}?{urlencode(params)}"
        request = Request(full_url, headers={"User-Agent": "TTRL-AI-Trading-OS/1.0"})
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _candle_from_kline(symbol: str, timeframe: Timeframe, item: list[Any]) -> Candle:
        return Candle(
            symbol=symbol,
            timeframe=timeframe,
            open=float(item[1]),
            high=float(item[2]),
            low=float(item[3]),
            close=float(item[4]),
            volume=float(item[5]),
            start_time_ms=int(item[0]),
            end_time_ms=int(item[6]),
        )

    @staticmethod
    def _whale_trade_from_agg(symbol: str, item: dict[str, Any]) -> WhaleTrade:
        price = float(item["p"])
        quantity = float(item["q"])
        side = "SELL" if bool(item.get("m", False)) else "BUY"
        timestamp_ms = int(item.get("T", 0) or 0)
        timestamp = (
            datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc).isoformat()
            if timestamp_ms
            else utc_now()
        )
        return WhaleTrade(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            timestamp=timestamp,
            source="binance_public_agg_trades",
        )
